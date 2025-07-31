# my_entrepreneur_platform/startups/models.py

from django.db import models
from django.conf import settings # To refer to the User model

class Industry(models.Model):
    """
    Categorizes startups by their industry (e.g., 'Fintech', 'AI', 'Healthcare').
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Industries"
        ordering = ['name']

    def __str__(self):
        return self.name

class Startup(models.Model):
    """
    Represents a startup or business profile on the platform.
    """
    STAGE_CHOICES = [
        ('IDEA', 'Idea Stage'),
        ('MVP', 'Minimum Viable Product'),
        ('SEED', 'Seed Funded'),
        ('GROWTH', 'Growth Stage'),
        ('OPERATING', 'Operating Business'),
        ('EXITED', 'Exited/Acquired'),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_startups',
        help_text="The main user who owns or manages this startup profile."
    )
    name = models.CharField(max_length=255, unique=True)
    tagline = models.CharField(max_length=255, blank=True, null=True, help_text="A short, catchy phrase for the startup.")
    description = models.TextField()
    industry = models.ForeignKey(
        Industry,
        on_delete=models.SET_NULL, # If an industry is deleted, startups keep it blank.
        related_name='startups',
        null=True,
        blank=True,
        help_text="The primary industry this startup belongs to."
    )
    stage = models.CharField(max_length=10, choices=STAGE_CHOICES, default='IDEA')
    funding_needs = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True,
        help_text="Current funding amount sought, if any."
    )
    website_url = models.URLField(blank=True, null=True)
    pitch_deck_url = models.URLField(blank=True, null=True, help_text="Link to presentation for investors.")
    logo = models.ImageField(upload_to='startup_logos/', blank=True, null=True)

    # Followers (Many-to-Many relationship with User model)
    # This allows users to "follow" a startup
    followers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='followed_startups',
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Startups" # Correct pluralization for admin
        ordering = ['name']

    def __str__(self):
        return self.name