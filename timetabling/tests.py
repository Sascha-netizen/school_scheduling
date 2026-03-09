from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from timetabling.models import Stage, Teacher, Subject, Room, ClassGroup, TimeSlot, Lesson


class AuthAndRolesTests(TestCase):
    """
    Tests for User Stories 1 & 4 — Authentication and Roles.
    Covers login success/failure and role-based access control
    for Teachers and Secretaries.
    """

    def setUp(self):
        """Create a teacher user and a secretary user with the correct groups."""
        self.client = Client()

        self.teachers_group = Group.objects.create(name='Teachers')
        self.secretaries_group = Group.objects.create(name='Secretaries')

        self.teacher_user = User.objects.create_user(
            username='teacher1', password='testpass123'
        )
        self.teacher_user.groups.add(self.teachers_group)

        self.secretary_user = User.objects.create_user(
            username='secretary1', password='secpass123'
        )
        self.secretary_user.groups.add(self.secretaries_group)

    def test_login_succeeds_with_valid_credentials(self):
        """A user with valid credentials should be redirected after login."""
        response = self.client.post(reverse('account_login'), {
            'login': 'teacher1',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)

    def test_login_fails_with_wrong_password(self):
        """A user with invalid credentials should stay on the login page."""
        response = self.client.post(reverse('account_login'), {
            'login': 'teacher1',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)

    def test_teacher_can_access_view_schedule(self):
        """A logged-in teacher should be able to access their schedule page."""
        self.client.login(username='teacher1', password='testpass123')
        response = self.client.get(reverse('view_schedule'))
        self.assertEqual(response.status_code, 200)

    def test_secretary_can_access_create_schedule(self):
        """A logged-in secretary should be able to access the schedule creation page."""
        self.client.login(username='secretary1', password='secpass123')
        response = self.client.get(reverse('create_schedule'))
        self.assertEqual(response.status_code, 200)

    def test_non_secretary_is_redirected_from_create_schedule(self):
        """A teacher (non-secretary) should be redirected away from schedule creation."""
        self.client.login(username='teacher1', password='testpass123')
        response = self.client.get(reverse('create_schedule'))
        self.assertRedirects(response, reverse('home'))

    def test_logged_out_user_cannot_access_view_schedule(self):
        """A logged-out user should be redirected when trying to access a protected page."""
        response = self.client.get(reverse('view_schedule'))
        self.assertEqual(response.status_code, 302)


class ScheduleCreationTests(TestCase):
    """
    Tests for User Stories 2 & 3 — Schedule Creation and Viewing by Stage.
    Covers the secretary's ability to create lessons using available system
    data, and to view schedules filtered by stage.
    """

    def setUp(self):
        """Create a secretary user and all the supporting data needed to build a lesson."""
        self.client = Client()

        self.secretaries_group = Group.objects.create(name='Secretaries')
        self.secretary_user = User.objects.create_user(
            username='secretary1', password='secpass123'
        )
        self.secretary_user.groups.add(self.secretaries_group)
        self.client.login(username='secretary1', password='secpass123')

        # Create two stages
        self.middle_school = Stage.objects.create(name='Middle School')
        self.high_school = Stage.objects.create(name='High School')

        # Create supporting data for Middle School
        self.teacher_user = User.objects.create_user(
            username='teacher1', password='testpass123'
        )
        self.teacher = Teacher.objects.create(
            user=self.teacher_user, stage=self.middle_school
        )
        self.subject = Subject.objects.create(
            name='Maths', stage=self.middle_school
        )
        self.room = Room.objects.create(
            name='Room 101', stage=self.middle_school
        )
        self.class_group = ClassGroup.objects.create(
            name='8b', stage=self.middle_school
        )
        self.timeslot = TimeSlot.objects.create(
            stage=self.middle_school,
            day='Monday',
            start_time='08:00',
            end_time='09:00',
        )

    def test_secretary_can_load_schedule_creation_page(self):
        """The schedule creation page should load successfully for a secretary."""
        response = self.client.get(reverse('create_schedule'))
        self.assertEqual(response.status_code, 200)

    def test_schedule_creation_page_contains_stages(self):
        """The schedule creation page should display the available stages."""
        response = self.client.get(reverse('create_schedule'))
        self.assertContains(response, 'Middle School')
        self.assertContains(response, 'High School')

    def test_secretary_can_create_a_lesson(self):
        """Submitting valid lesson data should create a new lesson in the database."""
        response = self.client.post(reverse('create_schedule'), {
            'stage': self.middle_school.id,
            'teacher': self.teacher.id,
            'subject': self.subject.id,
            'room': self.room.id,
            'class_group': self.class_group.id,
            'timeslot': self.timeslot.id,
            'save_lesson': True,
        })
        self.assertEqual(Lesson.objects.count(), 1)

    def test_admin_schedule_page_loads(self):
        """The admin schedule page should load for a staff member."""
        self.secretary_user.is_staff = True
        self.secretary_user.save()
        response = self.client.get(reverse('admin_schedule'))
        self.assertEqual(response.status_code, 200)

    def test_admin_schedule_shows_correct_lessons(self):
        """The admin schedule page should display created lessons."""
        Lesson.objects.create(
            teacher=self.teacher,
            subject=self.subject,
            room=self.room,
            class_group=self.class_group,
            timeslot=self.timeslot,
        )
        self.secretary_user.is_staff = True
        self.secretary_user.save()
        response = self.client.get(reverse('admin_schedule'))
        self.assertContains(response, 'Maths')


class DoubleBookingTests(TestCase):
    """
    Tests for User Story 5 — Double Booking Prevention.
    Covers the system's ability to prevent a teacher, room, or class group
    from being booked into more than one lesson at the same timeslot.
    """

    def setUp(self):
        """Create a secretary, a full set of supporting data, and an initial lesson."""
        self.client = Client()

        self.secretaries_group = Group.objects.create(name='Secretaries')
        self.secretary_user = User.objects.create_user(
            username='secretary1', password='secpass123'
        )
        self.secretary_user.groups.add(self.secretaries_group)
        self.client.login(username='secretary1', password='secpass123')

        self.stage = Stage.objects.create(name='Middle School')

        self.teacher_user = User.objects.create_user(
            username='teacher1', password='testpass123'
        )
        self.teacher = Teacher.objects.create(
            user=self.teacher_user, stage=self.stage
        )
        self.subject = Subject.objects.create(name='Maths', stage=self.stage)
        self.room = Room.objects.create(name='Room 101', stage=self.stage)
        self.class_group = ClassGroup.objects.create(name='8b', stage=self.stage)
        self.timeslot = TimeSlot.objects.create(
            stage=self.stage,
            day='Monday',
            start_time='08:00',
            end_time='09:00',
        )

        # Create a second room and class group for conflict testing
        self.room2 = Room.objects.create(name='Room 202', stage=self.stage)
        self.class_group2 = ClassGroup.objects.create(name='9a', stage=self.stage)

        # Create the initial lesson that all conflict tests will clash with
        self.existing_lesson = Lesson.objects.create(
            teacher=self.teacher,
            subject=self.subject,
            room=self.room,
            class_group=self.class_group,
            timeslot=self.timeslot,
        )

    def test_cannot_double_book_teacher(self):
        """Booking the same teacher into a second lesson at the same timeslot should fail."""
        from django.db import IntegrityError
        with self.assertRaises(Exception):
            Lesson.objects.create(
                teacher=self.teacher,       # same teacher
                subject=self.subject,
                room=self.room2,            # different room
                class_group=self.class_group2,  # different class group
                timeslot=self.timeslot,     # same timeslot
            )

    def test_cannot_double_book_room(self):
        """Booking the same room for a second lesson at the same timeslot should fail."""
        teacher_user2 = User.objects.create_user(
            username='teacher2', password='testpass123'
        )
        teacher2 = Teacher.objects.create(user=teacher_user2, stage=self.stage)
        with self.assertRaises(Exception):
            Lesson.objects.create(
                teacher=teacher2,
                subject=self.subject,
                room=self.room,             # same room
                class_group=self.class_group2,
                timeslot=self.timeslot,     # same timeslot
            )

    def test_cannot_double_book_class_group(self):
        """Booking the same class group into a second lesson at the same timeslot should fail."""
        teacher_user2 = User.objects.create_user(
            username='teacher2', password='testpass123'
        )
        teacher2 = Teacher.objects.create(user=teacher_user2, stage=self.stage)
        with self.assertRaises(Exception):
            Lesson.objects.create(
                teacher=teacher2,
                subject=self.subject,
                room=self.room2,
                class_group=self.class_group,   # same class group
                timeslot=self.timeslot,         # same timeslot
            )

    def test_valid_lesson_with_no_conflicts_is_saved(self):
        """A lesson with no conflicts should be created successfully."""
        teacher_user2 = User.objects.create_user(
            username='teacher2', password='testpass123'
        )
        teacher2 = Teacher.objects.create(user=teacher_user2, stage=self.stage)
        timeslot2 = TimeSlot.objects.create(
            stage=self.stage,
            day='Tuesday',
            start_time='08:00',
            end_time='09:00',
        )
        Lesson.objects.create(
            teacher=teacher2,
            subject=self.subject,
            room=self.room2,
            class_group=self.class_group2,
            timeslot=timeslot2,
        )
        self.assertEqual(Lesson.objects.count(), 2)


class ExportAndDisplayTests(TestCase):
    """
    Tests for User Story 6 — Timetable Display and CSV Export.
    Covers the display of timetables as HTML tables and the ability
    to export schedule data as a downloadable CSV file.
    """

    def setUp(self):
        """Create a secretary, a teacher, and a lesson to display and export."""
        self.client = Client()

        self.secretaries_group = Group.objects.create(name='Secretaries')
        self.teachers_group = Group.objects.create(name='Teachers')

        self.secretary_user = User.objects.create_user(
            username='secretary1', password='secpass123'
        )
        self.secretary_user.groups.add(self.secretaries_group)
        self.secretary_user.is_staff = True
        self.secretary_user.save()

        self.teacher_user = User.objects.create_user(
            username='teacher1', password='testpass123',
            first_name='Jane', last_name='Smith'
        )
        self.teacher_user.groups.add(self.teachers_group)

        self.stage = Stage.objects.create(name='Middle School')
        self.teacher = Teacher.objects.create(
            user=self.teacher_user, stage=self.stage
        )
        self.subject = Subject.objects.create(name='Maths', stage=self.stage)
        self.room = Room.objects.create(name='Room 101', stage=self.stage)
        self.class_group = ClassGroup.objects.create(name='8b', stage=self.stage)
        self.timeslot = TimeSlot.objects.create(
            stage=self.stage,
            day='Monday',
            start_time='08:00',
            end_time='09:00',
        )
        self.lesson = Lesson.objects.create(
            teacher=self.teacher,
            subject=self.subject,
            room=self.room,
            class_group=self.class_group,
            timeslot=self.timeslot,
        )

    def test_admin_schedule_displays_as_html_table(self):
        """The admin schedule page should render an HTML table containing lesson data."""
        self.client.login(username='secretary1', password='secpass123')
        response = self.client.get(reverse('admin_schedule'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<table')

    def test_admin_schedule_contains_lesson_data(self):
        """The admin schedule page should display the subject and room from the lesson."""
        self.client.login(username='secretary1', password='secpass123')
        response = self.client.get(reverse('admin_schedule'))
        self.assertContains(response, 'Maths')
        self.assertContains(response, 'Room 101')

    def test_csv_export_returns_correct_content_type(self):
        """The CSV export endpoint should return a file with the correct content type."""
        self.client.login(username='secretary1', password='secpass123')
        response = self.client.get(reverse('export_schedule_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')

    def test_csv_export_contains_lesson_data(self):
        """The exported CSV file should contain the lesson's subject and room."""
        self.client.login(username='secretary1', password='secpass123')
        response = self.client.get(reverse('export_schedule_csv'))
        content = response.content.decode('utf-8')
        self.assertIn('Maths', content)
        self.assertIn('Room 101', content)

    def test_teacher_csv_export_contains_own_lessons(self):
        """A teacher's personal CSV export should contain only their own lessons."""
        self.client.login(username='teacher1', password='testpass123')
        response = self.client.get(reverse('export_teacher_schedule_csv'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('Maths', content)

    def test_logged_out_user_cannot_export_csv(self):
        """A logged-out user should not be able to access the CSV export."""
        response = self.client.get(reverse('export_schedule_csv'))
        self.assertNotEqual(response.status_code, 200)


class DataComponentTests(TestCase):
    """
    Tests for User Story 7 — Handling Data Components.
    Covers the availability of core data entities (subjects, rooms,
    class groups, and timeslots) when creating a lesson.
    """

    def setUp(self):
        """Create a stage and a new subject belonging to it."""
        self.stage = Stage.objects.create(name='Middle School')
        self.subject = Subject.objects.create(name='Biology', stage=self.stage)

    def test_new_subject_is_immediately_available(self):
        """A newly created subject should be retrievable from the database."""
        subjects = Subject.objects.filter(stage=self.stage)
        self.assertIn(self.subject, subjects)