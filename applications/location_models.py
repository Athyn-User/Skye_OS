# File: applications/location_models.py
# Location schedule models for commercial property policies

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid

class PolicyLocation(models.Model):
    """Individual location under a commercial property policy"""
    
    CONSTRUCTION_TYPES = [
        ('frame', 'Frame'),
        ('joisted_masonry', 'Joisted Masonry'),
        ('non_combustible', 'Non-Combustible'),
        ('masonry_non_combustible', 'Masonry Non-Combustible'),
        ('modified_fire_resistive', 'Modified Fire Resistive'),
        ('fire_resistive', 'Fire Resistive'),
    ]
    
    OCCUPANCY_TYPES = [
        ('office', 'Office'),
        ('retail', 'Retail'),
        ('warehouse', 'Warehouse'),
        ('manufacturing', 'Manufacturing'),
        ('restaurant', 'Restaurant'),
        ('apartment', 'Apartment'),
        ('mixed_use', 'Mixed Use'),
        ('other', 'Other'),
    ]
    
    SPRINKLER_TYPES = [
        ('none', 'No Sprinklers'),
        ('partial', 'Partial Sprinklers'),
        ('full_wet', 'Full Wet System'),
        ('full_dry', 'Full Dry System'),
        ('deluge', 'Deluge System'),
    ]
    
    # Basic identification
    location_id = models.AutoField(primary_key=True)
    policy = models.ForeignKey('Policy', on_delete=models.CASCADE, related_name='locations')
    location_number = models.CharField(max_length=10, help_text="Location identifier (e.g., 001, 002)")
    location_name = models.CharField(max_length=200, blank=True, help_text="Optional location name/description")
    
    # Address information - VISIBLE PHASE 1
    street_address = models.CharField(max_length=200)
    address_line_2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=10)
    county = models.CharField(max_length=100, blank=True)
    
    # Basic coverage limits - VISIBLE PHASE 1
    building_limit = models.DecimalField(
        max_digits=12, decimal_places=2, 
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Building coverage limit"
    )
    contents_limit = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Contents coverage limit"
    )
    
    # Advanced building details - HIDDEN INITIALLY
    construction_type = models.CharField(
        max_length=30, choices=CONSTRUCTION_TYPES, blank=True,
        help_text="Building construction classification"
    )
    year_built = models.IntegerField(
        blank=True, null=True,
        validators=[MinValueValidator(1800), MaxValueValidator(2030)]
    )
    square_footage = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(1)])
    number_of_stories = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(1)])
    basement = models.BooleanField(default=False)
    
    # Occupancy details - HIDDEN INITIALLY
    primary_occupancy = models.CharField(max_length=30, choices=OCCUPANCY_TYPES, blank=True)
    occupancy_description = models.TextField(blank=True, help_text="Detailed occupancy description")
    
    # Advanced coverage limits - HIDDEN INITIALLY
    business_income_limit = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True,
        validators=[MinValueValidator(Decimal('0'))]
    )
    extra_expense_limit = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True,
        validators=[MinValueValidator(Decimal('0'))]
    )
    
    # Deductibles - HIDDEN INITIALLY
    building_deductible = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True,
        validators=[MinValueValidator(Decimal('0'))]
    )
    contents_deductible = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True,
        validators=[MinValueValidator(Decimal('0'))]
    )
    
    # Coinsurance - HIDDEN INITIALLY
    building_coinsurance = models.IntegerField(
        blank=True, null=True,
        validators=[MinValueValidator(50), MaxValueValidator(100)],
        help_text="Building coinsurance percentage"
    )
    contents_coinsurance = models.IntegerField(
        blank=True, null=True,
        validators=[MinValueValidator(50), MaxValueValidator(100)],
        help_text="Contents coinsurance percentage"
    )
    
    # Protection features - HIDDEN INITIALLY
    sprinkler_system = models.CharField(
        max_length=20, choices=SPRINKLER_TYPES, default='none'
    )
    burglar_alarm = models.BooleanField(default=False)
    fire_alarm = models.BooleanField(default=False)
    security_guard = models.BooleanField(default=False)
    
    # Special conditions - HIDDEN INITIALLY
    flood_zone = models.CharField(max_length=10, blank=True)
    earthquake_zone = models.CharField(max_length=10, blank=True)
    environmental_hazards = models.TextField(blank=True)
    special_conditions = models.TextField(blank=True, help_text="Special underwriting conditions")
    
    # Status and metadata
    is_active = models.BooleanField(default=True)
    effective_date = models.DateField(help_text="Date location became effective")
    termination_date = models.DateField(blank=True, null=True)
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'policy_locations'
        ordering = ['location_number']
        unique_together = ['policy', 'location_number']
        indexes = [
            models.Index(fields=['policy', 'location_number']),
            models.Index(fields=['policy', 'is_active']),
        ]
    
    def __str__(self):
        return f"Loc {self.location_number}: {self.street_address}, {self.city}, {self.state}"
    
    @property
    def full_address(self):
        """Return complete formatted address"""
        address_parts = [self.street_address]
        if self.address_line_2:
            address_parts.append(self.address_line_2)
        address_parts.append(f"{self.city}, {self.state} {self.zip_code}")
        return '\n'.join(address_parts)
    
    @property
    def total_limit(self):
        """Return total building + contents limit"""
        return (self.building_limit or 0) + (self.contents_limit or 0)
    
    def clean(self):
        """Custom validation"""
        from django.core.exceptions import ValidationError
        
        if self.building_limit <= 0 and self.contents_limit <= 0:
            raise ValidationError("At least one coverage limit must be greater than zero")
        
        if self.termination_date and self.termination_date <= self.effective_date:
            raise ValidationError("Termination date must be after effective date")


class LocationSchedule(models.Model):
    """Groups locations into schedules for endorsements"""
    
    SCHEDULE_TYPES = [
        ('all_locations', 'All Locations'),
        ('selected_locations', 'Selected Locations'),
        ('locations_by_state', 'Locations by State'),
        ('locations_by_occupancy', 'Locations by Occupancy'),
        ('custom', 'Custom Schedule'),
    ]
    
    schedule_id = models.AutoField(primary_key=True)
    policy = models.ForeignKey('Policy', on_delete=models.CASCADE, related_name='location_schedules')
    schedule_name = models.CharField(max_length=200, help_text="Descriptive name for this schedule")
    schedule_type = models.CharField(max_length=30, choices=SCHEDULE_TYPES)
    
    # Schedule criteria (for automatic inclusion)
    include_states = models.CharField(max_length=200, blank=True, help_text="Comma-separated state codes")
    include_occupancies = models.CharField(max_length=200, blank=True, help_text="Comma-separated occupancy types")
    min_limit = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    max_limit = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    
    # Display options
    show_building_limits = models.BooleanField(default=True)
    show_contents_limits = models.BooleanField(default=True)
    show_deductibles = models.BooleanField(default=False)
    show_construction_details = models.BooleanField(default=False)
    show_protection_features = models.BooleanField(default=False)
    
    # Totals
    total_building_limit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_contents_limit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_locations = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'location_schedules'
        ordering = ['schedule_name']
    
    def __str__(self):
        return f"{self.schedule_name} ({self.total_locations} locations)"
    
    def calculate_totals(self):
        """Calculate and update schedule totals"""
        items = self.items.select_related('location').filter(location__is_active=True)
        
        self.total_building_limit = sum([item.location.building_limit or 0 for item in items])
        self.total_contents_limit = sum([item.location.contents_limit or 0 for item in items])
        self.total_locations = items.count()
        self.save(update_fields=['total_building_limit', 'total_contents_limit', 'total_locations'])
    
    def add_locations_by_criteria(self):
        """Automatically add locations based on schedule criteria"""
        if self.schedule_type == 'all_locations':
            locations = self.policy.locations.filter(is_active=True)
        elif self.schedule_type == 'locations_by_state' and self.include_states:
            states = [s.strip() for s in self.include_states.split(',')]
            locations = self.policy.locations.filter(is_active=True, state__in=states)
        elif self.schedule_type == 'locations_by_occupancy' and self.include_occupancies:
            occupancies = [o.strip() for o in self.include_occupancies.split(',')]
            locations = self.policy.locations.filter(is_active=True, primary_occupancy__in=occupancies)
        else:
            return  # Manual selection required
        
        # Apply limit filters
        if self.min_limit:
            locations = locations.filter(
                models.Q(building_limit__gte=self.min_limit) | 
                models.Q(contents_limit__gte=self.min_limit)
            )
        if self.max_limit:
            locations = locations.filter(
                building_limit__lte=self.max_limit,
                contents_limit__lte=self.max_limit
            )
        
        # Create schedule items
        for location in locations:
            LocationScheduleItem.objects.get_or_create(
                schedule=self,
                location=location,
                defaults={'sequence_order': self.items.count() + 1}
            )
        
        self.calculate_totals()


class LocationScheduleItem(models.Model):
    """Individual location within a schedule"""
    
    item_id = models.AutoField(primary_key=True)
    schedule = models.ForeignKey(LocationSchedule, on_delete=models.CASCADE, related_name='items')
    location = models.ForeignKey(PolicyLocation, on_delete=models.CASCADE)
    sequence_order = models.IntegerField(help_text="Order within the schedule")
    
    # Override display values if needed
    display_name = models.CharField(max_length=200, blank=True, help_text="Override location description")
    notes = models.TextField(blank=True, help_text="Special notes for this item in schedule")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'location_schedule_items'
        ordering = ['sequence_order']
        unique_together = ['schedule', 'location']
    
    def __str__(self):
        return f"{self.schedule.schedule_name} - {self.location}"


class LocationEndorsement(models.Model):
    """Links location schedules to specific endorsements"""
    
    endorsement_id = models.AutoField(primary_key=True)
    policy = models.ForeignKey('Policy', on_delete=models.CASCADE)
    endorsement_document = models.ForeignKey(
        'EndorsementDocument', 
        on_delete=models.CASCADE, 
        related_name='location_endorsements',
        blank=True, null=True
    )
    schedule = models.ForeignKey(LocationSchedule, on_delete=models.CASCADE)
    
    # Endorsement details
    endorsement_number = models.CharField(max_length=50)
    effective_date = models.DateField()
    description = models.TextField(blank=True)
    
    # Action type
    ACTION_TYPES = [
        ('add_locations', 'Add Locations'),
        ('remove_locations', 'Remove Locations'),
        ('modify_limits', 'Modify Limits'),
        ('update_schedule', 'Update Schedule'),
    ]
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'location_endorsements'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.endorsement_number} - {self.get_action_type_display()}"