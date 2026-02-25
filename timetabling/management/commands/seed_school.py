from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from timetabling.models import Teacher, Subject, Room, ClassGroup, TimeSlot, Stage


class Command(BaseCommand):
    help = 'Seeds the database with Middle and High School test data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')

        # -------------------------
        # STAGES
        # -------------------------
        middle, _ = Stage.objects.get_or_create(name='Middle School')
        high, _ = Stage.objects.get_or_create(name='High School')

        # -------------------------
        # TIMESLOTS
        # -------------------------
        slot_data = [
            ('Monday', '08:00', '09:00'),
            ('Monday', '09:00', '10:00'),
            ('Monday', '10:15', '11:15'),
            ('Monday', '11:15', '12:15'),
            ('Monday', '13:15', '14:15'),
            ('Tuesday', '08:00', '09:00'),
            ('Tuesday', '09:00', '10:00'),
            ('Tuesday', '10:15', '11:15'),
            ('Tuesday', '11:15', '12:15'),
            ('Tuesday', '13:15', '14:15'),
            ('Wednesday', '08:00', '09:00'),
            ('Wednesday', '09:00', '10:00'),
            ('Wednesday', '10:15', '11:15'),
            ('Wednesday', '11:15', '12:15'),
            ('Wednesday', '13:15', '14:15'),
            ('Thursday', '08:00', '09:00'),
            ('Thursday', '09:00', '10:00'),
            ('Thursday', '10:15', '11:15'),
            ('Thursday', '11:15', '12:15'),
            ('Thursday', '13:15', '14:15'),
            ('Friday', '08:00', '09:00'),
            ('Friday', '09:00', '10:00'),
            ('Friday', '10:15', '11:15'),
            ('Friday', '11:15', '12:15'),
            ('Friday', '13:15', '14:15'),
        ]

        for stage in [middle, high]:
            for day, start, end in slot_data:
                TimeSlot.objects.get_or_create(
                    day=day,
                    start_time=start,
                    end_time=end,
                    stage=stage
                )
        self.stdout.write('  Timeslots created.')

        # -------------------------
        # MIDDLE SCHOOL
        # -------------------------
        # Users and Teachers
        middle_teachers = [
            ('Alice', 'Johnson'),
            ('Bob', 'Smith'),
            ('Carol', 'White'),
            ('David', 'Green'),
        ]
        middle_teacher_objs = []
        for first, last in middle_teachers:
            user, _ = User.objects.get_or_create(username=f"{first.lower()}.{last.lower()}")
            teacher, _ = Teacher.objects.get_or_create(user=user, stage=middle)
            middle_teacher_objs.append(teacher)
        self.stdout.write('  Middle School teachers created.')

        # Subjects
        Subject.objects.get_or_create(name='Maths', stage=middle)
        Subject.objects.get_or_create(name='Art', stage=middle)
        Subject.objects.get_or_create(name='English', stage=middle)
        Subject.objects.get_or_create(name='Science', stage=middle)
        Subject.objects.get_or_create(name='History', stage=middle)
        self.stdout.write('  Middle School subjects created.')

        # Rooms
        for name in ['Room 101', 'Room 102', 'Room 103']:
            Room.objects.get_or_create(name=name, stage=middle)
        self.stdout.write('  Middle School rooms created.')

        # ClassGroups
        for name in ['6A', '6B', '7A']:
            ClassGroup.objects.get_or_create(name=name, stage=middle)
        self.stdout.write('  Middle School class groups created.')

        # -------------------------
        # HIGH SCHOOL
        # -------------------------
        high_teachers = [
            ('Emily', 'Brown'),
            ('Frank', 'Adams'),
            ('Grace', 'Lee'),
            ('Henry', 'Wilson'),
            ('Ivy', 'Clark'),
        ]
        high_teacher_objs = []
        for first, last in high_teachers:
            user, _ = User.objects.get_or_create(username=f"{first.lower()}.{last.lower()}")
            teacher, _ = Teacher.objects.get_or_create(user=user, stage=high)
            high_teacher_objs.append(teacher)
        self.stdout.write('  High School teachers created.')

        # Subjects
        Subject.objects.get_or_create(name='Maths', stage=high)
        Subject.objects.get_or_create(name='English', stage=high)
        Subject.objects.get_or_create(name='Physics', stage=high)
        Subject.objects.get_or_create(name='Chemistry', stage=high)
        Subject.objects.get_or_create(name='History', stage=high)
        Subject.objects.get_or_create(name='Biology', stage=high)
        self.stdout.write('  High School subjects created.')

        # Rooms
        for name in ['Room 201', 'Room 202', 'Room 203', 'Room 204']:
            Room.objects.get_or_create(name=name, stage=high)
        self.stdout.write('  High School rooms created.')

        # ClassGroups
        for name in ['10A', '10B', '11A', '11B']:
            ClassGroup.objects.get_or_create(name=name, stage=high)
        self.stdout.write('  High School class groups created.')

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))