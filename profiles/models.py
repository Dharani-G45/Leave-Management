from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = [
        ('Student', 'Student'),
        ('Staff', 'Staff'),
        ('Reporting Person', 'Reporting Person'), 
        ('HR', 'HR'),
        ('Founder', 'Founder'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='Student') # Increased max_length to 20
    id_number = models.CharField(max_length=50, unique=True, verbose_name="ID")
    email = models.EmailField(max_length=254)
    branch_department = models.CharField(max_length=100, verbose_name="Branch/Dept")
    image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    dob = models.DateField(blank=True, null=True, verbose_name="Date of Birth")

    reporting_person = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True, 
        related_name='team_members',
        limit_choices_to={'role__in': ['Staff', 'Reporting Person', 'HR', 'Founder']}
    )

    def __str__(self):
        return f"{self.user.get_full_name() if self.user.get_full_name() else self.user.username} ({self.role})"