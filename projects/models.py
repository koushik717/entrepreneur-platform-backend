# my_entrepreneur_platform/projects/models.py

from django.db import models
from django.conf import settings # To refer to the User model
from startups.models import Startup # Import the Startup model

class Technology(models.Model):
    """
    Represents a technology or skill used in a project.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Technologies"
        ordering = ['name']

    def __str__(self):
        return self.name

class Project(models.Model):
    """
    Represents an individual project or initiative by a user or startup.
    """
    STATUS_CHOICES = [
        ('IDEA', 'Idea Stage'),
        ('PLANNING', 'Planning Phase'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('SEEKING_FUNDING', 'Seeking Funding'),
        ('PAUSED', 'Paused'),
    ]

    LOOKING_FOR_CHOICES = [
        ('COFOUNDERS', 'Co-Founders'),
        ('MENTORS', 'Mentors'),
        ('INVESTORS', 'Investors'),
        ('EARLY_ADOPTERS', 'Early Adopters'),
        ('TALENT', 'Talent/Team Members'),
        ('PARTNERSHIPS', 'Partnerships'),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects',
        help_text="The user who owns or is leading this project."
    )
    related_startup = models.ForeignKey(
        Startup,
        on_delete=models.SET_NULL, # If startup is deleted, project remains but link is cleared.
        related_name='projects',
        null=True,
        blank=True,
        help_text="Optional: The startup this project belongs to."
    )
    title = models.CharField(max_length=255)
    tagline = models.CharField(max_length=255, blank=True, null=True, help_text="A short, catchy phrase for the project.")
    description = models.TextField()
    project_logo = models.ImageField(upload_to='project_logos/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IDEA')
    technologies_used = models.ManyToManyField(
        Technology,
        related_name='projects',
        blank=True,
        help_text="Technologies or skills utilized in this project."
    )
    looking_for = models.CharField(
        max_length=20,
        choices=LOOKING_FOR_CHOICES,
        blank=True,
        null=True,
        help_text="What the project is currently seeking (e.g., co-founders, funding)."
    )
    link_to_repo = models.URLField(blank=True, null=True, help_text="Link to the project's code repository.")
    link_to_demo = models.URLField(blank=True, null=True, help_text="Link to a live demo or prototype.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Projects"
        ordering = ['-created_at'] # Newest projects first

    def __str__(self):
        return self.title