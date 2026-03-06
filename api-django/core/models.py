from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class Users(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('researcher', 'Researcher'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='researcher')
    
    # Separate name fields
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    suffix = models.CharField(max_length=20, blank=True, null=True)
    
    # Keep full_name for backward compatibility and easy querying
    full_name = models.CharField(max_length=255, editable=False)
    
    # Use email as the primary identifier
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_blocked = models.BooleanField(default=False)
    
    # Use email for authentication instead of username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def save(self, *args, **kwargs):
        # Auto-generate username from email if not provided
        if not self.username:
            self.username = self.email.split('@')[0]
            # Make sure username is unique
            counter = 1
            original_username = self.username
            while Users.objects.filter(username=self.username).exists():
                self.username = f"{original_username}_{counter}"
                counter += 1
        
        # Auto-generate full_name before saving
        self.full_name = self.get_full_name()
        super().save(*args, **kwargs)
    
    def get_full_name(self):
        """Generate full name from individual name components"""
        name_parts = [self.first_name]
        
        # Add middle name if it exists and is not empty
        if self.middle_name and self.middle_name.strip():
            name_parts.append(self.middle_name.strip())
        
        name_parts.append(self.last_name)
        
        # Add suffix if it exists and is not empty
        if self.suffix and self.suffix.strip():
            name_parts.append(self.suffix.strip())
        
        return ' '.join(name_parts)
    
    def __str__(self):
        return f"{self.full_name} ({self.email})"
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_researcher(self):
        return self.role == 'researcher'

    @property
    def firstName(self):
        return self.first_name

    @firstName.setter
    def firstName(self, value):
        self.first_name = value

    @property
    def lastName(self):
        return self.last_name

    @lastName.setter
    def lastName(self, value):
        self.last_name = value

    @property
    def middleName(self):
        return self.middle_name

    @middleName.setter
    def middleName(self, value):
        self.middle_name = value

    @property
    def fullName(self):
        return self.full_name

    @property
    def createdAt(self):
        return self.created_at

    @property
    def updatedAt(self):
        return self.updated_at

    @property
    def isBlocked(self):
        return self.is_blocked

    @isBlocked.setter
    def isBlocked(self, value):
        self.is_blocked = value

# Passport Data Related Models
class Location(models.Model):
    country = models.TextField(blank=True, null=True)
    province = models.TextField(blank=True, null=True)
    nearest_town = models.TextField(blank=True, null=True)
    barangay = models.TextField(blank=True, null=True)
    purok_or_sitio = models.TextField(blank=True, null=True)
    latitude = models.CharField(max_length=30, blank=True, null=True)
    longitude = models.CharField(max_length=30, blank=True, null=True)
    altitude = models.CharField(max_length=30, blank=True, null=True)
    
    def __str__(self):
        location_parts = []
        if self.barangay:
            location_parts.append(f"Brgy. {self.barangay}")
        if self.nearest_town:
            location_parts.append(self.nearest_town)
        if self.province:
            location_parts.append(self.province)
        if self.country:
            location_parts.append(self.country)
        return ", ".join(location_parts) if location_parts else f"Location {self.id}"


class Crop(models.Model):
    crop_group = models.TextField(blank=True, null=True)
    crop_name = models.TextField(blank=True, null=True)
    genus = models.TextField(blank=True, null=True)
    species = models.TextField(blank=True, null=True)
    species_authority = models.TextField(blank=True, null=True)
    subtaxon = models.TextField(blank=True, null=True)
    subtaxon_authority = models.TextField(blank=True, null=True)
    local_name = models.TextField(blank=True, null=True)
    accession_name = models.TextField(blank=True, null=True)
    other_crop_name = models.TextField(blank=True, null=True)
    biologicalStatus = models.TextField(blank=True, null=True)
    storage = models.TextField(blank=True, null=True)
    samplingMethod = models.TextField(blank=True, null=True)
    materialCollected = models.TextField(blank=True, null=True)
    sampleType = models.TextField(blank=True,null=True)
    def __str__(self):
        if self.crop_name:
            return self.crop_name
        elif self.genus and self.species:
            return f"{self.genus} {self.species}"
        else:
            return f"Crop {self.id}"


class Donor(models.Model):
    growers_name = models.TextField(blank=True, null=True)
    growers_contact_number = models.CharField(max_length=50, blank=True, null=True)
    donor_code = models.CharField(max_length=50, blank=True, null=True)
    donor_accession_number = models.CharField(max_length=50, blank=True, null=True)
    donor_name = models.TextField(blank=True, null=True)
    location_duplicate_site = models.TextField(blank=True, null=True)
    duplicate_institution_name = models.TextField(blank=True, null=True)
    other_donor_code_name = models.TextField(blank=True, null=True)
    
    def __str__(self):
        if self.donor_name:
            return self.donor_name
        elif self.growers_name:
            return self.growers_name
        else:
            return f"Donor {self.id}"


class Topography(models.Model):
    cultural_practice = models.TextField(blank=True, null=True)
    herbarium_specimen = models.BooleanField(default=False)
    topography = models.TextField(blank=True, null=True)
    site = models.TextField(blank=True, null=True)
    soil_texture = models.TextField(blank=True, null=True)
    soil_color = models.TextField(blank=True, null=True)
    drainage = models.TextField(blank=True, null=True)
    stoniness = models.TextField(blank=True, null=True)
    diseases_and_pests = models.TextField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Topography {self.id} - {self.site or 'No site specified'}"


class Availability(models.Model):
    available_at_in_vitro = models.BooleanField(default=False)
    available_in_the_field = models.BooleanField(default=False)
    available_for_distribution = models.BooleanField(default=False)
    status_of_harvest = models.TextField(blank=True, null=True)
    characterized = models.TextField(blank=True, null=True)
    field = models.TextField(blank=True, null=True)
    
    def __str__(self):
        status = []
        if self.available_at_in_vitro:
            status.append("In Vitro")
        if self.available_in_the_field:
            status.append("Field")
        if self.available_for_distribution:
            status.append("Distribution")
        return f"Availability {self.id} - {', '.join(status) if status else 'None'}"


class Photo(models.Model):
    passport_data = models.ForeignKey('PassportData', on_delete=models.CASCADE, blank=True, null=True, related_name='photos')
    photo = models.ImageField(upload_to='passport_photos/', blank=True, null=True)
    photo_name = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.photo_name or f"Photo {self.id}"

    @property
    def photoName(self):
        return self.photo_name

    @photoName.setter
    def photoName(self, value):
        self.photo_name = value

    @property
    def uploadedAt(self):
        return self.uploaded_at


class PassportData(models.Model):
    collection_country_code = models.CharField(max_length=10, blank=True, null=True)
    accession_number = models.CharField(max_length=50, blank=True, null=True)
    old_accession_number = models.CharField(max_length=50, blank=True, null=True)
    gb_number = models.CharField(max_length=50, blank=True, null=True)
    collection_number = models.CharField(max_length=50, blank=True, null=True)
    collecting_date = models.DateField(blank=True, null=True)
    acquisition_date = models.DateField(blank=True, null=True)
    collector = models.TextField(blank=True, null=True)
    
    # Foreign keys
    location = models.ForeignKey(Location, on_delete=models.CASCADE, blank=True, null=True)
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, blank=True, null=True)
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, blank=True, null=True)
    topography = models.ForeignKey(Topography, on_delete=models.CASCADE, blank=True, null=True)
    availability = models.ForeignKey(Availability, on_delete=models.CASCADE, blank=True, null=True)
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, blank=True, null=True)
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(Users, on_delete=models.SET_NULL, blank=True, null=True, related_name='created_passportdata')
    updated_by = models.ForeignKey(Users, on_delete=models.SET_NULL, blank=True, null=True, related_name='updated_passportdata')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Passport Data'
        verbose_name_plural = 'Passport Data'
    
    def __str__(self):
        if self.accession_number:
            return f"Passport Data - {self.accession_number}"
        else:
            return f"Passport Data {self.id}"

    @property
    def collectionCountryCode(self):
        return self.collection_country_code

    @collectionCountryCode.setter
    def collectionCountryCode(self, value):
        self.collection_country_code = value

    @property
    def accessionNumber(self):
        return self.accession_number

    @accessionNumber.setter
    def accessionNumber(self, value):
        self.accession_number = value

    @property
    def oldAccessionNumber(self):
        return self.old_accession_number

    @oldAccessionNumber.setter
    def oldAccessionNumber(self, value):
        self.old_accession_number = value

    @property
    def gbNumber(self):
        return self.gb_number

    @gbNumber.setter
    def gbNumber(self, value):
        self.gb_number = value

    @property
    def collectionNumber(self):
        return self.collection_number

    @collectionNumber.setter
    def collectionNumber(self, value):
        self.collection_number = value

    @property
    def collectingDate(self):
        return self.collecting_date

    @collectingDate.setter
    def collectingDate(self, value):
        self.collecting_date = value

    @property
    def acquisitionDate(self):
        return self.acquisition_date

    @acquisitionDate.setter
    def acquisitionDate(self, value):
        self.acquisition_date = value

    @property
    def createdAt(self):
        return self.created_at

    @property
    def updatedAt(self):
        return self.updated_at

    @property
    def createdBy(self):
        return self.created_by

    @createdBy.setter
    def createdBy(self, value):
        self.created_by = value

    @property
    def updatedBy(self):
        return self.updated_by

    @updatedBy.setter
    def updatedBy(self, value):
        self.updated_by = value


class Usage(models.Model):
    passport_data = models.ForeignKey(PassportData, on_delete=models.CASCADE, related_name='usages')
    plant_part = models.TextField(blank=True, null=True)
    usage_description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Usage for {self.passport_data} - {self.plant_part or 'Unknown part'}"

    @property
    def passportData(self):
        return self.passport_data

    @passportData.setter
    def passportData(self, value):
        self.passport_data = value

    @property
    def plantPart(self):
        return self.plant_part

    @plantPart.setter
    def plantPart(self, value):
        self.plant_part = value

    @property
    def usageDescription(self):
        return self.usage_description

    @usageDescription.setter
    def usageDescription(self, value):
        self.usage_description = value


class Customer(models.Model):
    customerName = models.TextField()
    designation = models.TextField(blank=True, null=True)
    office = models.TextField(blank=True, null=True)
    contactInfo = models.CharField(max_length=20, blank=True, null=True)
    emailAddress = models.TextField(blank=True, null=True)
    updatedBy = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_customers')

class Product(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True)
    crop = models.ForeignKey(Crop, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    material = models.TextField(blank=True, null=True)
    unitPrice = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    photo = models.BinaryField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    createdBy = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_products')
    updatedBy = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_products')
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

class Regeneration(models.Model):
    regenerationReferenceNo = models.TextField(blank=True, null=True)
    activeBase = models.TextField(blank=True, null=True)
    sowingDate = models.DateField(blank=True, null=True)
    harvestDate = models.DateField(blank=True, null=True)
    plotNo = models.TextField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    seedsPerPlot = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    rowsPerPlot = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    seedsPerRow = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    distanceBetweenHills = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    distanceBetweenRows = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    distanceBetweenPlots = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fertilization = models.TextField(blank=True, null=True)
    numPlantsEstablished = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    mannerOfPollination = models.TextField(blank=True, null=True)
    culturalPracticeTrellis = models.BooleanField(default=False)
    culturalPracticeMulchPlastic = models.BooleanField(default=False)
    culturalPracticeMulchRiceHull = models.BooleanField(default=False)
    culturalPracticeMulchCoirDust = models.BooleanField(default=False)
    culturalPracticeMulchSawDust = models.BooleanField(default=False)
    culturalPracticeIrrigation = models.TextField(blank=True, null=True)
    createdBy = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_regenerations')
    updatedBy = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_regenerations')
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

class SeedLot(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    regenerationBatch = models.ForeignKey(Regeneration, on_delete=models.SET_NULL, null=True, blank=True)
    lotCode = models.CharField(max_length=100, unique=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    quantityUnit = models.CharField(max_length=20, blank=True, null=True)
    harvestDate = models.DateField(blank=True, null=True)
    storageLocation = models.TextField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    lotStatus = models.CharField(max_length=20, choices=[('AVAILABLE','AVAILABLE'),('EXHAUSTED','EXHAUSTED'),('EXPIRED','EXPIRED'),('QUARANTINED','QUARANTINED')], blank=True, null=True)
    isViable = models.BooleanField(default=False)
    viabilityTestDate = models.DateField(blank=True, null=True)
    germinationRate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    seedCondition = models.TextField(blank=True, null=True)
    processingMethod = models.TextField(blank=True, null=True)
    createdBy = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_seedlots')
    updatedBy = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_seedlots')
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.lotCode} - {self.quantity} {self.quantityUnit or 'units'}"

class StockMovements(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    regenerationBatch = models.ForeignKey(Regeneration, on_delete=models.SET_NULL, null=True, blank=True)
    seedLot = models.ForeignKey(SeedLot, on_delete=models.SET_NULL, null=True, blank=True)
    movementType = models.CharField(max_length=20, choices=[('ACQUISITION','ACQUISITION'),('DISPOSAL','DISPOSAL'),('STOCK_TAKE','STOCK_TAKE'),('DISTRIBUTION','DISTRIBUTION')])
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.TextField(blank=True, null=True)
    movementDate = models.DateField()
    dateUpdated = models.DateField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    shelfNo = models.TextField(blank=True, null=True)
    trayNo = models.TextField(blank=True, null=True)
    bottleNo = models.TextField(blank=True, null=True)
    packetNo = models.TextField(blank=True, null=True)
    activeBase = models.TextField(blank=True, null=True)
    batchReference = models.TextField(blank=True, null=True)
    pollType = models.TextField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    dateOfRegeneration = models.DateField(blank=True, null=True)
    quarter = models.TextField(blank=True, null=True)
    createdBy = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_stockmovements')
    updatedBy = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_stockmovements')
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)


class Request(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    purpose = models.TextField(blank=True, null=True)
    cropName = models.TextField(blank=True, null=True)
    useOfMaterials = models.TextField(blank=True, null=True)
    projectTitle = models.TextField(blank=True, null=True)
    materialNeeded = models.TextField(blank=True, null=True)
    supplyName = models.TextField(blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    unit = models.TextField(blank=True, null=True)
    requestDate = models.DateField()
    approved = models.BooleanField(default=False)
    approvedDate = models.DateField(blank=True, null=True)
    approvedBy = models.TextField(blank=True, null=True)
    released = models.BooleanField(default=False)
    releasedDate = models.DateField(blank=True, null=True)
    releasedBy = models.TextField(blank=True, null=True)
    quarterReleased = models.TextField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True)
    seedLot = models.ForeignKey(SeedLot, on_delete=models.SET_NULL, null=True, blank=True)
    sourceAcquisition = models.ForeignKey(StockMovements, on_delete=models.SET_NULL, null=True, blank=True, related_name='requests_from_acquisition')
    createdBy = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_requests')
    updatedBy = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_requests')
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)


class AkapulkoCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='akapulko_characteristics')

    growth_habit = models.TextField(blank=True, null=True)
    branching_habit = models.TextField(blank=True, null=True)
    plant_height_aboveground_m = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    plant_span_spread_m = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    internode_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stem_diameter_base_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    leaflet_shape = models.TextField(blank=True, null=True)
    leaflet_apex = models.TextField(blank=True, null=True)
    leaf_color_rhs = models.TextField(blank=True, null=True)
    leaf_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_width_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_length_width_ratio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaflet_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaflet_width_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaflet_length_width_ratio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    petiole_color_rhs = models.TextField(blank=True, null=True)
    petiole_width_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    date_of_first_flowering = models.DateField(blank=True, null=True)
    flower_color_rhs = models.TextField(blank=True, null=True)
    infloresence_position = models.TextField(blank=True, null=True)
    bract_size = models.TextField(blank=True, null=True)

    pod_color = models.TextField(blank=True, null=True)
    pod_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pod_size_variability = models.TextField(blank=True, null=True)
    pod_ridge = models.TextField(blank=True, null=True)
    pod_luster_dark_stage = models.TextField(blank=True, null=True)
    ease_of_seed_extraction = models.TextField(blank=True, null=True)

    seed_color_rhs = models.TextField(blank=True, null=True)
    seed_surface = models.TextField(blank=True, null=True)
    seed_length_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    seed_width_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    hundred_seed_weight_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    photo = models.ImageField(upload_to='akapulko_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Akapulko Characteristics {self.id}"


class BananaCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='banana_characteristics')

    leaf_habit = models.TextField(blank=True, null=True)
    dwarfism = models.TextField(blank=True, null=True)
    pseudostem_height_m = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pseudostem_aspect = models.TextField(blank=True, null=True)
    pseudostem_colour = models.TextField(blank=True, null=True)
    pseudostem_appearance = models.TextField(blank=True, null=True)
    predominant_underlying_colour_of_pseudostem = models.TextField(blank=True, null=True)
    pigmentation_of_underlying_pseudostem = models.TextField(blank=True, null=True)
    sap_colour = models.TextField(blank=True, null=True)
    wax_on_leaf_sheaths = models.TextField(blank=True, null=True)
    number_of_suckers = models.IntegerField(blank=True, null=True)
    development_of_suckers = models.TextField(blank=True, null=True)
    position_of_suckers = models.TextField(blank=True, null=True)

    petiole_or_midrib_or_leaf = models.TextField(blank=True, null=True)
    blotches_at_petiole_base = models.TextField(blank=True, null=True)
    blotches_colour = models.TextField(blank=True, null=True)
    petiole_canal_leaf_iii = models.TextField(blank=True, null=True)
    petiole_margins = models.TextField(blank=True, null=True)
    wing_type = models.TextField(blank=True, null=True)
    petiole_margin_colour = models.TextField(blank=True, null=True)
    edge_of_petiole_margin = models.TextField(blank=True, null=True)
    petiole_margin_width_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_blade_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_blade_width_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_ratio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    petiole_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    colour_of_leaf_upper_surface = models.TextField(blank=True, null=True)
    appearance_of_leaf_upper_surface = models.TextField(blank=True, null=True)
    colour_of_leaf_lower_surface = models.TextField(blank=True, null=True)
    appearance_of_leaf_lower_surface = models.TextField(blank=True, null=True)
    wax_on_leaves = models.TextField(blank=True, null=True)
    insertion_point_of_leaf_blades_on_petiole = models.TextField(blank=True, null=True)
    shape_of_leaf_blade_base = models.TextField(blank=True, null=True)
    leaf_corrugation = models.TextField(blank=True, null=True)
    colour_of_midrib_dorsal_surface = models.TextField(blank=True, null=True)
    colour_of_midrib_ventral_surface = models.TextField(blank=True, null=True)
    colour_of_cigar_leaf_dorsal_surface = models.TextField(blank=True, null=True)
    blotches_on_leaves_of_water_suckers = models.TextField(blank=True, null=True)

    peduncle_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    empty_nodes_on_peduncle = models.IntegerField(blank=True, null=True)
    peduncle_width_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    peduncle_colour = models.TextField(blank=True, null=True)
    peduncle_hairiness = models.TextField(blank=True, null=True)
    bunch_position = models.TextField(blank=True, null=True)
    bunch_shape = models.TextField(blank=True, null=True)
    bunch_appearance = models.TextField(blank=True, null=True)
    flowers_that_form_fruit = models.TextField(blank=True, null=True)
    fruits = models.TextField(blank=True, null=True)
    rachis_type = models.TextField(blank=True, null=True)
    rachis_position = models.TextField(blank=True, null=True)
    rachis_appearance = models.TextField(blank=True, null=True)
    male_bud_type = models.TextField(blank=True, null=True)
    male_bud_shape = models.TextField(blank=True, null=True)
    male_bud_size_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    bract_base_shape = models.TextField(blank=True, null=True)
    bract_apex_shape = models.TextField(blank=True, null=True)
    bract_imbrication = models.TextField(blank=True, null=True)
    colour_of_bract_external_face = models.TextField(blank=True, null=True)
    colour_of_bract_internal_face = models.TextField(blank=True, null=True)
    colour_on_bract_apex = models.TextField(blank=True, null=True)
    colour_stripes_on_bract = models.TextField(blank=True, null=True)
    bract_scars_on_rachis = models.TextField(blank=True, null=True)
    fading_of_colour_on_bract_base = models.TextField(blank=True, null=True)
    male_bract_shape = models.TextField(blank=True, null=True)
    male_bract_lifting = models.TextField(blank=True, null=True)
    bract_behaviour_before_falling = models.TextField(blank=True, null=True)
    wax_on_bract = models.TextField(blank=True, null=True)
    presence_of_grooves_on_bract = models.TextField(blank=True, null=True)
    male_flower_behaviour = models.TextField(blank=True, null=True)

    compound_tepal_basic_colour = models.TextField(blank=True, null=True)
    compound_tepal_pigmentation = models.TextField(blank=True, null=True)
    lobe_colour_of_compound_tepal = models.TextField(blank=True, null=True)
    lobe_development_of_compound_tepal = models.TextField(blank=True, null=True)
    free_tepal_colour = models.TextField(blank=True, null=True)
    free_tepal_shape = models.TextField(blank=True, null=True)
    free_tepal_appearance = models.TextField(blank=True, null=True)
    free_tepal_apex_development = models.TextField(blank=True, null=True)
    free_tepal_apex_shape = models.TextField(blank=True, null=True)
    anther_exsertion = models.TextField(blank=True, null=True)
    filament_colour = models.TextField(blank=True, null=True)
    anther_colour = models.TextField(blank=True, null=True)
    pollen_sac_colour = models.TextField(blank=True, null=True)
    pollen_vitality_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    style_basic_colour = models.TextField(blank=True, null=True)
    pigmentation_on_style = models.TextField(blank=True, null=True)
    style_exsertion = models.TextField(blank=True, null=True)
    style_shape = models.TextField(blank=True, null=True)
    stigma_colour = models.TextField(blank=True, null=True)
    ovary_shape = models.TextField(blank=True, null=True)
    ovary_basic_colour = models.TextField(blank=True, null=True)
    ovary_pigmentation = models.TextField(blank=True, null=True)
    dominant_colour_of_male_flower = models.TextField(blank=True, null=True)
    irregular_flowers = models.TextField(blank=True, null=True)
    arrangement_of_ovules = models.TextField(blank=True, null=True)

    fruit_position = models.TextField(blank=True, null=True)
    number_of_fruits = models.IntegerField(blank=True, null=True)
    fruit_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_shape_longitudinal_curvature = models.TextField(blank=True, null=True)
    transverse_section_of_fruit = models.TextField(blank=True, null=True)
    fruit_apex = models.TextField(blank=True, null=True)
    remains_of_flower_relicts_at_fruit_apex = models.TextField(blank=True, null=True)
    fruit_pedicel_length_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_pedicel_width_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pedicel_surface = models.TextField(blank=True, null=True)
    fusion_of_pedicels = models.TextField(blank=True, null=True)
    immature_fruit_peel_colour = models.TextField(blank=True, null=True)
    mature_fruit_peel_colour = models.TextField(blank=True, null=True)
    fruit_peel_thickness_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    adherence_of_fruit_peel = models.TextField(blank=True, null=True)
    cracks_in_fruit_peel = models.TextField(blank=True, null=True)
    pulp_in_fruit = models.TextField(blank=True, null=True)
    pulp_colour_before_maturity = models.TextField(blank=True, null=True)
    pulp_colour_at_maturity = models.TextField(blank=True, null=True)
    fruits_fall_from_hands = models.TextField(blank=True, null=True)
    flesh_texture = models.TextField(blank=True, null=True)
    predominant_taste = models.TextField(blank=True, null=True)
    presence_of_seed_with_source_of_pollen = models.TextField(blank=True, null=True)
    seed_surface = models.TextField(blank=True, null=True)
    seed_shape = models.TextField(blank=True, null=True)

    photo = models.ImageField(upload_to='banana_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Banana Characteristics {self.id}"


class BittergourdCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='bittergourd_characteristics')

    plot_no = models.TextField(blank=True, null=True)
    sowing_date = models.DateField(blank=True, null=True)
    transplanting_date = models.DateField(blank=True, null=True)

    days_to_emergence = models.IntegerField(blank=True, null=True)
    cotyledon_size = models.TextField(blank=True, null=True)
    cotyledon_color = models.TextField(blank=True, null=True)
    internode_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stem_shape = models.TextField(blank=True, null=True)
    tendrils = models.TextField(blank=True, null=True)
    leaf_shape = models.TextField(blank=True, null=True)
    leaf_size = models.TextField(blank=True, null=True)
    color_of_leaf_spots_or_checks = models.TextField(blank=True, null=True)
    leaf_margin = models.TextField(blank=True, null=True)
    leaf_lobes = models.TextField(blank=True, null=True)
    leaf_pubescence_dorsal_surface = models.TextField(blank=True, null=True)
    leaf_pubescence_ventral_side = models.TextField(blank=True, null=True)
    plant_growth_habit = models.TextField(blank=True, null=True)

    time_of_maturity = models.TextField(blank=True, null=True)
    days_to_flowering = models.IntegerField(blank=True, null=True)
    flower_color = models.TextField(blank=True, null=True)
    flower_seed = models.TextField(blank=True, null=True)
    sex_type = models.TextField(blank=True, null=True)

    peduncle_transectional_shape = models.TextField(blank=True, null=True)
    peduncle_attachment = models.TextField(blank=True, null=True)
    peduncle_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    peduncle_separation_from_fruit = models.TextField(blank=True, null=True)
    stem_end_fruit_shape = models.TextField(blank=True, null=True)
    blossom_end_fruit_shape = models.TextField(blank=True, null=True)
    fruit_shape = models.TextField(blank=True, null=True)
    fruit_ribs = models.TextField(blank=True, null=True)
    fruit_rib_shape = models.TextField(blank=True, null=True)
    fruit_size_variability = models.TextField(blank=True, null=True)
    fruit_color_at_maturity = models.TextField(blank=True, null=True)
    fruit_color_intensity = models.TextField(blank=True, null=True)
    fruit_skin_texture = models.TextField(blank=True, null=True)
    fruit_skin_texture_intensity = models.TextField(blank=True, null=True)
    fruit_lustre = models.TextField(blank=True, null=True)
    fruit_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_width_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_weight_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_breadth = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    flesh_thickness = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cavity_diameter = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    flesh_color = models.TextField(blank=True, null=True)
    flesh_color_intensity = models.TextField(blank=True, null=True)
    flesh_moisture = models.TextField(blank=True, null=True)
    flesh_texture = models.TextField(blank=True, null=True)
    intensity_of_bitterness_of_flesh = models.TextField(blank=True, null=True)
    amount_of_placental_tissue = models.TextField(blank=True, null=True)
    ease_of_seed_and_placenta_separation_from_flesh = models.TextField(blank=True, null=True)
    cracking_at_blossom_end = models.TextField(blank=True, null=True)

    number_of_seeds_per_fruit = models.IntegerField(blank=True, null=True)
    seed_surface = models.TextField(blank=True, null=True)
    seed_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    seed_width = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    seed_thickness = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    hundred_seed_weight_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    photo = models.ImageField(upload_to='bittergourd_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Bittergourd Characteristics {self.id}"


class BottlegourdCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='bottlegourd_characteristics')

    plot_no = models.TextField(blank=True, null=True)
    sowing_date = models.DateField(blank=True, null=True)
    transplanting_date = models.DateField(blank=True, null=True)
    species = models.TextField(blank=True, null=True)

    cotyledon_size = models.TextField(blank=True, null=True)
    cotyledon_color = models.TextField(blank=True, null=True)
    days_from_sowing_to_emergence = models.IntegerField(blank=True, null=True)
    internode_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stem_shape = models.TextField(blank=True, null=True)
    tendrils = models.TextField(blank=True, null=True)
    leaf_shape = models.TextField(blank=True, null=True)
    leaf_size = models.TextField(blank=True, null=True)
    color_of_leaf_spots_or_checks = models.TextField(blank=True, null=True)
    leaf_margin = models.TextField(blank=True, null=True)
    leaf_lobes = models.TextField(blank=True, null=True)
    leaf_pubescence_dorsal_surface = models.TextField(blank=True, null=True)
    leaf_pubescence_ventral_side = models.TextField(blank=True, null=True)
    plant_growth_habit = models.TextField(blank=True, null=True)

    time_of_maturity = models.TextField(blank=True, null=True)
    days_to_flowering = models.IntegerField(blank=True, null=True)
    flower_color = models.TextField(blank=True, null=True)
    flower_seed = models.TextField(blank=True, null=True)
    sex_type = models.TextField(blank=True, null=True)

    peduncle_transectional_shape = models.TextField(blank=True, null=True)
    peduncle_attachment = models.TextField(blank=True, null=True)
    peduncle_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    peduncle_separation_from_fruit = models.TextField(blank=True, null=True)
    stem_end_fruit_shape = models.TextField(blank=True, null=True)
    blossom_end_fruit_shape = models.TextField(blank=True, null=True)
    fruit_shape = models.TextField(blank=True, null=True)
    fruit_ribs = models.TextField(blank=True, null=True)
    fruit_rib_shape = models.TextField(blank=True, null=True)
    fruit_size_variability = models.TextField(blank=True, null=True)
    predominant_fruit_skin_color_at_maturity = models.TextField(blank=True, null=True)
    secondary_fruit_skin_color = models.TextField(blank=True, null=True)
    fruit_skin_color_intensity = models.TextField(blank=True, null=True)
    design_produced_by_secondary_fruit_skin_color = models.TextField(blank=True, null=True)
    fruit_skin_texture = models.TextField(blank=True, null=True)
    fruit_skin_texture_intensity = models.TextField(blank=True, null=True)
    fruit_lustre = models.TextField(blank=True, null=True)
    fruit_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_width_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_weight_kg = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_skin_hardness = models.TextField(blank=True, null=True)
    fruit_skin_thickness = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    flesh_thickness = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    flesh_color = models.TextField(blank=True, null=True)
    flesh_color_intensity = models.TextField(blank=True, null=True)
    flesh_moisture = models.TextField(blank=True, null=True)
    flesh_texture = models.TextField(blank=True, null=True)
    amount_of_placental_tissue = models.TextField(blank=True, null=True)
    ease_of_seed_and_placenta_separation_from_flesh = models.TextField(blank=True, null=True)
    flesh_flavor = models.TextField(blank=True, null=True)

    number_of_seeds_per_fruit = models.IntegerField(blank=True, null=True)
    seed_surface = models.TextField(blank=True, null=True)
    seed_surface_lustre = models.TextField(blank=True, null=True)
    seed_color = models.TextField(blank=True, null=True)
    hundred_seed_weight_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    photo = models.ImageField(upload_to='bottlegourd_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Bottlegourd Characteristics {self.id}"


class CashewCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='cashew_characteristics')

    plot_no = models.TextField(blank=True, null=True)
    sowing_date = models.DateField(blank=True, null=True)
    tree_habit = models.TextField(blank=True, null=True)
    tree_height_m = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tree_spread = models.TextField(blank=True, null=True)
    cracks_on_trunk_bark = models.TextField(blank=True, null=True)
    height_of_main_branches_m = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    crotch_angle_of_main_branches = models.TextField(blank=True, null=True)
    ease_of_peeling_bark_from_twigs = models.TextField(blank=True, null=True)
    extension_growth_of_twigs_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    branching_pattern = models.TextField(blank=True, null=True)
    twig_diameter = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    internode_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    number_of_leaves_per_twig = models.IntegerField(blank=True, null=True)
    color_of_young_leaves = models.TextField(blank=True, null=True)
    color_of_mature_leaves_at_harvest = models.TextField(blank=True, null=True)
    leaf_shape = models.TextField(blank=True, null=True)
    odor_of_leaves = models.TextField(blank=True, null=True)
    leaf_margin = models.TextField(blank=True, null=True)
    leaf_apex_shape = models.TextField(blank=True, null=True)
    leaf_size = models.TextField(blank=True, null=True)
    brittleness_of_leaf = models.TextField(blank=True, null=True)
    angle_of_leaf_petiole_relative_to_stem = models.TextField(blank=True, null=True)
    leaf_cross_section = models.TextField(blank=True, null=True)

    season_of_flowering = models.TextField(blank=True, null=True)
    infloresence_shape = models.TextField(blank=True, null=True)
    flower_color = models.TextField(blank=True, null=True)
    color_of_leaf_boot = models.TextField(blank=True, null=True)
    infloresence_size = models.TextField(blank=True, null=True)
    compactness_of_infloresence = models.TextField(blank=True, null=True)
    type_of_infloresence_branching = models.TextField(blank=True, null=True)
    elaboration_of_infloresence = models.TextField(blank=True, null=True)
    sex_ratio = models.TextField(blank=True, null=True)
    secondary_flowering = models.TextField(blank=True, null=True)

    mature_cashew_apple_color = models.TextField(blank=True, null=True)
    cashew_apple_shape = models.TextField(blank=True, null=True)
    size_of_cashew_apple = models.TextField(blank=True, null=True)
    weight_of_cashew_apple = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    shape_of_cashew_apple_base = models.TextField(blank=True, null=True)
    ridges_on_cashew_apple = models.TextField(blank=True, null=True)
    cashew_apple_apex = models.TextField(blank=True, null=True)
    grooves_on_apex = models.TextField(blank=True, null=True)
    cavity_at_apex_of_cashew_apple = models.TextField(blank=True, null=True)
    lenticel_size = models.TextField(blank=True, null=True)
    density_of_lenticels = models.TextField(blank=True, null=True)
    skin_of_cashew_apple = models.TextField(blank=True, null=True)
    ease_of_peeling_of_cashew_apple = models.TextField(blank=True, null=True)
    flesh_color = models.TextField(blank=True, null=True)
    flesh_softness = models.TextField(blank=True, null=True)
    flesh_odor = models.TextField(blank=True, null=True)
    juice_yield = models.TextField(blank=True, null=True)
    juice_astringency = models.TextField(blank=True, null=True)
    juice_acidity = models.TextField(blank=True, null=True)
    juice_sweetness = models.TextField(blank=True, null=True)
    attachment_of_nut_to_cashew_apple = models.TextField(blank=True, null=True)

    color_of_mature_nut_shell = models.TextField(blank=True, null=True)
    nut_shape = models.TextField(blank=True, null=True)
    nut_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    nut_width = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    nut_thickness = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    nut_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    shape_of_nut_base = models.TextField(blank=True, null=True)
    suture_of_nut = models.TextField(blank=True, null=True)
    flanks_of_nut = models.TextField(blank=True, null=True)
    stylar_scar_of_nut = models.TextField(blank=True, null=True)
    shape_of_nut_apex = models.TextField(blank=True, null=True)
    relative_position_of_suture_and_apex = models.TextField(blank=True, null=True)
    shell_pericarp_thickness_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    uniformity_of_thickness_excluding_suture = models.TextField(blank=True, null=True)
    shell_oil_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    shelling_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    kernel_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    kernel_width = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    kernel_thickness = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    seed_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    attachment_of_peel_to_kernel = models.TextField(blank=True, null=True)
    cotyledonary_grooves = models.TextField(blank=True, null=True)
    breakage_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    kernel_quality = models.TextField(blank=True, null=True)
    kernel_oil_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    kernel_protein_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    photo = models.ImageField(upload_to='cashew_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Cashew Characteristics {self.id}"


class CassavaCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='cassava_characteristics')

    plot_no = models.TextField(blank=True, null=True)
    sowing_date = models.DateField(blank=True, null=True)
    transplanting_date = models.DateField(blank=True, null=True)
    percent_germination_of_stakes = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    initial_vigor = models.TextField(blank=True, null=True)
    time_to_first_apical_branching = models.TextField(blank=True, null=True)
    time_to_second_apical_branching = models.TextField(blank=True, null=True)
    color_of_apical_leaves = models.TextField(blank=True, null=True)
    pubescence_of_young_leaf = models.TextField(blank=True, null=True)
    leaf_retention = models.TextField(blank=True, null=True)
    shape_of_central_lobe = models.TextField(blank=True, null=True)
    number_of_leaf_lobes = models.IntegerField(blank=True, null=True)
    length_of_central_lobe_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    width_of_central_lobe_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    lobe_margins = models.TextField(blank=True, null=True)
    petiole_color = models.TextField(blank=True, null=True)
    distribution_of_anthocyanin_pigment_in_petiole = models.TextField(blank=True, null=True)
    orientation_of_petiole = models.TextField(blank=True, null=True)
    petiole_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_color = models.TextField(blank=True, null=True)
    leaf_vein_color = models.TextField(blank=True, null=True)

    flowers = models.TextField(blank=True, null=True)
    color_of_sepal = models.TextField(blank=True, null=True)
    color_of_disc = models.TextField(blank=True, null=True)
    color_of_stigma = models.TextField(blank=True, null=True)
    color_of_ovary = models.TextField(blank=True, null=True)
    color_of_anthers = models.TextField(blank=True, null=True)

    prominence_of_leaf_scars = models.TextField(blank=True, null=True)
    distance_between_leaf_scars = models.TextField(blank=True, null=True)
    color_of_stem_cortex = models.TextField(blank=True, null=True)
    color_of_stem_epidermis = models.TextField(blank=True, null=True)
    stem_color = models.TextField(blank=True, null=True)
    growth_habit_of_stem = models.TextField(blank=True, null=True)
    color_of_end_branches_of_adult_plant = models.TextField(blank=True, null=True)
    length_of_stipules = models.TextField(blank=True, null=True)
    stipule_margin = models.TextField(blank=True, null=True)
    length_of_stipules_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    height_to_first_branching_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    number_of_levels_of_branching = models.IntegerField(blank=True, null=True)
    branching_habit = models.TextField(blank=True, null=True)
    angle_of_branching = models.TextField(blank=True, null=True)
    plant_form = models.TextField(blank=True, null=True)
    height_of_plant_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    fruit = models.TextField(blank=True, null=True)
    seed = models.TextField(blank=True, null=True)
    number_of_storage_roots_per_plant = models.IntegerField(blank=True, null=True)
    number_of_commercial_roots_per_plant = models.IntegerField(blank=True, null=True)
    extent_of_root_peduncle = models.TextField(blank=True, null=True)
    position_of_roots = models.TextField(blank=True, null=True)
    storage_root_form = models.TextField(blank=True, null=True)
    storage_root_constrictions = models.TextField(blank=True, null=True)
    root_constrictions = models.TextField(blank=True, null=True)
    texture_of_root_epidermis = models.TextField(blank=True, null=True)
    external_storage_root_surface_color = models.TextField(blank=True, null=True)
    storage_root_pulp_color_parenchyma = models.TextField(blank=True, null=True)
    storage_root_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    storage_root_diameter_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_fresh_weight_of_storage_roots_per_plant_kg = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ease_of_root_periderm_outer_skin_peeling = models.TextField(blank=True, null=True)
    ease_of_root_cortex_inner_skin_peeling = models.TextField(blank=True, null=True)
    color_of_outer_surface_of_storage_root_cortex = models.TextField(blank=True, null=True)
    root_taste = models.TextField(blank=True, null=True)
    estimate_of_storage_root_cyanide_content = models.TextField(blank=True, null=True)
    storage_root_dry_matter_percentage_dm = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    glycoalkaloid_dw_basis = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    oxalate_percent = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    amylose = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    starch_content_percent = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    photo = models.ImageField(upload_to='cassava_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Cassava Characteristics {self.id}"


class CitronellaCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='citronella_characteristics')

    plant_height_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    plant_growth_habit = models.TextField(blank=True, null=True)
    culm_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    culm_color = models.TextField(blank=True, null=True)
    leaf_sheath_color = models.TextField(blank=True, null=True)
    leaf_blade_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_blade_width_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_blade_lw_ratio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_blade_color = models.TextField(blank=True, null=True)
    number_of_days_to_flower_initiation = models.IntegerField(blank=True, null=True)
    inflorescence_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    inflorescence_type = models.TextField(blank=True, null=True)
    number_of_days_to_seed_maturation = models.IntegerField(blank=True, null=True)
    seed_yield_per_plant_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    characterized_by = models.TextField(blank=True, null=True)

    photo = models.ImageField(upload_to='citronella_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Citronella Characteristics {self.id}"


class CornCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='corn_characteristics')

    date_planted = models.DateField(blank=True, null=True)
    plot_no = models.TextField(blank=True, null=True)

    days_to_emergence = models.IntegerField(blank=True, null=True)
    days_to_tasseling = models.IntegerField(blank=True, null=True)
    days_to_silking = models.IntegerField(blank=True, null=True)
    days_to_harvest = models.IntegerField(blank=True, null=True)

    anthocyanin_coloration_of_shealth = models.TextField(blank=True, null=True)
    shape_of_apex = models.TextField(blank=True, null=True)
    intensity_of_green_color = models.TextField(blank=True, null=True)
    tillering_index = models.TextField(blank=True, null=True)
    undulation_of_margin_of_blade = models.TextField(blank=True, null=True)
    stem_color = models.TextField(blank=True, null=True)
    sheath_pubescence = models.TextField(blank=True, null=True)
    total_number_of_leaves_per_plant = models.IntegerField(blank=True, null=True)
    leaf_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_width = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_orientation = models.TextField(blank=True, null=True)
    prescence_of_leaf_ligule = models.TextField(blank=True, null=True)
    angle_between_blade_and_stem = models.TextField(blank=True, null=True)
    curvature_of_blade = models.TextField(blank=True, null=True)
    venation_index = models.TextField(blank=True, null=True)
    degree_of_stem_zigzag = models.TextField(blank=True, null=True)
    anthocyanin_coloration_at_base_of_glume = models.TextField(blank=True, null=True)
    anthocyanin_coloration_of_glumes_excluding_base = models.TextField(blank=True, null=True)
    anthocyanin_coloration_of_anthers = models.TextField(blank=True, null=True)
    tassel_type_at_milk_stage = models.TextField(blank=True, null=True)
    angle_between_main_axis_and_lateral_branches_of_tassel = models.TextField(blank=True, null=True)
    curvature_of_lateral_branches_of_tassel = models.TextField(blank=True, null=True)
    tassel_color = models.TextField(blank=True, null=True)
    density_of_spikelets_of_tassel = models.TextField(blank=True, null=True)
    anthocyanin_coloration_of_silks = models.TextField(blank=True, null=True)
    silk_color = models.TextField(blank=True, null=True)

    plant_height = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ear_height = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    number_of_leaves_above_the_uppermost_ear_including_ear_leaf = models.IntegerField(blank=True, null=True)
    number_of_leaves_below_uppermost_ear_including_ear_leaf = models.IntegerField(blank=True, null=True)
    anthocyanin_coloration_of_leaf_shealth = models.TextField(blank=True, null=True)
    number_of_internodes_below_uppermost_ear = models.IntegerField(blank=True, null=True)
    number_of_internodes_below_on_the_whole_stem = models.IntegerField(blank=True, null=True)
    anthocyanin_coloration_of_internodes = models.TextField(blank=True, null=True)
    stem_diameter_below_uppermost_ear = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stem_daimeter_at_the_base = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    anthocyanin_coloration_of_brace_roots = models.TextField(blank=True, null=True)

    tassel_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    length_of_main_axis_above_lowest_lateral_branch = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    length_of_main_axis_above_highest_lateral_branch = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    length_of_lateral_branch = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tassel_peduncle_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tassel_branching_space = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    number_of_primary_branches_on_tassel = models.IntegerField(blank=True, null=True)
    number_of_secondary_branches_on_tassel = models.IntegerField(blank=True, null=True)
    number_of_tertiary_branches_on_tassel = models.IntegerField(blank=True, null=True)

    stay_green = models.TextField(blank=True, null=True)
    days_to_ear_leaf_inflorescence = models.IntegerField(blank=True, null=True)
    stalk_lodging = models.TextField(blank=True, null=True)
    husk_cover = models.TextField(blank=True, null=True)
    husk_fitting = models.TextField(blank=True, null=True)
    husk_tip_shape = models.TextField(blank=True, null=True)
    ear_shape = models.TextField(blank=True, null=True)
    ear_tip_shape = models.TextField(blank=True, null=True)
    ear_orientation = models.TextField(blank=True, null=True)
    anthocyanin_coloration_of_glumes_of_cob = models.TextField(blank=True, null=True)
    number_of_bracts = models.IntegerField(blank=True, null=True)
    kernel_row_arrangement = models.TextField(blank=True, null=True)
    number_of_kernels_rows = models.IntegerField(blank=True, null=True)
    number_of_kernels_per_row = models.IntegerField(blank=True, null=True)
    ear_damage = models.TextField(blank=True, null=True)
    unshelled_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ear_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    peduncle_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ear_diameter = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cob_diameter = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    rachis_diameter = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cob_color = models.TextField(blank=True, null=True)
    shelled_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    percent_grain_shedding = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    thousand_kernel_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    kernel_type = models.TextField(blank=True, null=True)
    kernel_color = models.TextField(blank=True, null=True)
    kernel_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    kernel_width = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    kernel_thickness = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    shape_of_upper_kernel_surface = models.TextField(blank=True, null=True)
    pericarp_color = models.TextField(blank=True, null=True)
    aleurone_color = models.TextField(blank=True, null=True)
    endosperm_color = models.TextField(blank=True, null=True)

    photo = models.ImageField(upload_to='corn_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Corn Characteristics {self.id}"


class CowpeaCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='cowpea_characteristics')

    plot_no = models.TextField(blank=True, null=True)
    date_planted = models.DateField(blank=True, null=True)
    days_to_emergence = models.IntegerField(blank=True, null=True)
    hypocotyl_color = models.TextField(blank=True, null=True)
    hypocotyl_length_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    plant_vigour = models.TextField(blank=True, null=True)
    number_of_nodes_on_the_main_stem = models.IntegerField(blank=True, null=True)
    growth_pattern = models.TextField(blank=True, null=True)
    growth_habit = models.TextField(blank=True, null=True)
    twining_tendency = models.TextField(blank=True, null=True)
    plant_pigmentation = models.TextField(blank=True, null=True)
    terminal_leaflet_shape = models.TextField(blank=True, null=True)
    leaf_colour = models.TextField(blank=True, null=True)
    leaf_marking = models.TextField(blank=True, null=True)
    terminal_leaflet_length_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    terminal_leaflet_width_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_texture = models.TextField(blank=True, null=True)
    stipule_length_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stipule_width_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    plant_hairiness = models.TextField(blank=True, null=True)
    number_of_main_branches = models.IntegerField(blank=True, null=True)
    days_to_flowering = models.IntegerField(blank=True, null=True)
    raceme_position = models.TextField(blank=True, null=True)
    flower_pigment_pattern = models.TextField(blank=True, null=True)
    flower_keel_colour = models.TextField(blank=True, null=True)
    flower_standard_colour = models.TextField(blank=True, null=True)
    flower_wing_colour = models.TextField(blank=True, null=True)
    standard_petal_length_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    calyx_lobed_length_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    duration_of_flowering = models.TextField(blank=True, null=True)
    number_of_raceme_per_plant = models.IntegerField(blank=True, null=True)
    peduncle_length_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    number_of_pods_per_peduncle = models.IntegerField(blank=True, null=True)
    plant_height_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    days_to_first_mature_pods = models.IntegerField(blank=True, null=True)
    pod_attachment_to_peduncle = models.TextField(blank=True, null=True)
    immature_pod_pigmentation = models.TextField(blank=True, null=True)
    pod_curvature_mature_pods = models.TextField(blank=True, null=True)
    number_of_locules_per_pod = models.IntegerField(blank=True, null=True)
    pod_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pod_width_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pericarp_thickness = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pod_color_mature_pods = models.TextField(blank=True, null=True)
    seed_shape = models.TextField(blank=True, null=True)
    testa_texture = models.TextField(blank=True, null=True)
    seed_main_color = models.TextField(blank=True, null=True)
    seed_predominant_secondary_color = models.TextField(blank=True, null=True)
    seed_length_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    seed_width_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    seed_thickness_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    seed_crowding = models.TextField(blank=True, null=True)
    splitting_of_testa = models.TextField(blank=True, null=True)
    attachment_of_testa = models.TextField(blank=True, null=True)
    number_of_pods_per_plant = models.IntegerField(blank=True, null=True)
    yield_per_plant_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ten_pod_weight_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    number_of_seeds_per_pod = models.IntegerField(blank=True, null=True)
    percentage_of_first_harvest = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    hundred_seed_weight_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    photo = models.ImageField(upload_to='cowpea_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Cowpea Characteristics {self.id}"


class EggplantCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='eggplant_characteristics')

    sowing_date = models.DateField(blank=True, null=True)
    transplanting_date = models.DateField(blank=True, null=True)
    plot_no = models.TextField(blank=True, null=True)
    number_of_days_to_50_percent_germination = models.IntegerField(blank=True, null=True)
    anthocyanin_coloration_of_hypocotyl = models.TextField(blank=True, null=True)
    intensity_of_anthocyanin_coloration = models.TextField(blank=True, null=True)
    cotyledonous_leaf_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cotyledonous_leaf_width = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cotyledonous_leaf_color = models.TextField(blank=True, null=True)
    cotyledon_length_over_width_ratio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    plant_growth_habit = models.TextField(blank=True, null=True)
    plant_height_at_flowering_stage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    plant_breadth_at_flowering_stage_in = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    plant_branching = models.TextField(blank=True, null=True)
    stem_anthocyanin_coloration = models.TextField(blank=True, null=True)
    stem_intensity_of_anthocyanin_coloration = models.TextField(blank=True, null=True)
    stem_pubescence = models.TextField(blank=True, null=True)
    petiole_color = models.TextField(blank=True, null=True)
    petiole_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_blade_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_blade_width = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_blade_lobing = models.TextField(blank=True, null=True)
    leaf_blade_tip_angle = models.TextField(blank=True, null=True)
    leaf_blade_color_upper_surface = models.TextField(blank=True, null=True)
    leaf_blade_intensity_of_green_color = models.TextField(blank=True, null=True)
    leaf_blade_blistering = models.TextField(blank=True, null=True)
    leaf_prickles = models.TextField(blank=True, null=True)
    leaf_hairs = models.TextField(blank=True, null=True)
    numbers_of_flowers_per_inflorescence = models.IntegerField(blank=True, null=True)
    flower_size = models.TextField(blank=True, null=True)
    number_of_days_from_sowing_till_first_flower = models.IntegerField(blank=True, null=True)
    number_of_hermaphrodite_flowers_per_inflorescence = models.IntegerField(blank=True, null=True)
    corolla_color = models.TextField(blank=True, null=True)
    intensity_of_purple_color_of_flower = models.TextField(blank=True, null=True)
    relative_style_length_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pollen_production = models.TextField(blank=True, null=True)
    fruit_length_from_base_to_calyx_to_tip_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_breadth_diameter_at_broadest_part_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_length_breadth_ratio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_curvature = models.TextField(blank=True, null=True)
    fruit_pedicel_length_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_pedicel_thickness_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_pedicel_prickles = models.TextField(blank=True, null=True)
    fruit_shape_widest_part = models.TextField(blank=True, null=True)
    general_fruit_shape = models.TextField(blank=True, null=True)
    fruit_apex_shape = models.TextField(blank=True, null=True)
    fruit_skin_color_at_commercial_ripeness = models.TextField(blank=True, null=True)
    fruit_skin_color_distribution_at_commercial_ripeness = models.TextField(blank=True, null=True)
    fruit_skin_color_at_physiological_ripeness = models.TextField(blank=True, null=True)
    fruit_patches = models.TextField(blank=True, null=True)
    fruit_stripe = models.TextField(blank=True, null=True)
    fruit_position = models.TextField(blank=True, null=True)
    relative_fruit_calyx_length_n_10 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_calyx_prickles_n_10 = models.TextField(blank=True, null=True)
    creasing_of_calyx = models.TextField(blank=True, null=True)
    fruit_cross_section = models.TextField(blank=True, null=True)
    fruit_flesh_color = models.TextField(blank=True, null=True)
    number_of_locules_per_fruit = models.IntegerField(blank=True, null=True)
    fruit_flesh_density = models.TextField(blank=True, null=True)
    number_of_fruit_per_infructescence = models.IntegerField(blank=True, null=True)
    number_of_fruits_per_plant = models.IntegerField(blank=True, null=True)
    fruit_yield_per_plant_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_flavor = models.TextField(blank=True, null=True)
    seed_color = models.TextField(blank=True, null=True)
    seed_size = models.TextField(blank=True, null=True)
    thousand_seed_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    photo = models.ImageField(upload_to='eggplant_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Eggplant Characteristics {self.id}"


class FruitsCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='fruits_characteristics')

    date_harvested = models.DateField(blank=True, null=True)
    date_evaluated = models.DateField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    age_of_tree_years = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tree_height_m = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    trunk_height_m = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    trunk_circumference_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    trunk_surface = models.TextField(blank=True, null=True)
    tree_vigor = models.TextField(blank=True, null=True)
    tree_growth_habit = models.TextField(blank=True, null=True)
    branching_density = models.TextField(blank=True, null=True)
    branching_pattern = models.TextField(blank=True, null=True)
    crown_shape = models.TextField(blank=True, null=True)
    leaf_blade_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_blade_width_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_blade_length_width_ratio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_blade_shape = models.TextField(blank=True, null=True)
    presence_of_leaf_pubescence = models.TextField(blank=True, null=True)
    petiole_length_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    flowering_precocity = models.TextField(blank=True, null=True)
    inflorence_color = models.TextField(blank=True, null=True)
    flowering_ability = models.TextField(blank=True, null=True)
    fruiting_ability = models.TextField(blank=True, null=True)
    years_to_first_fruiting = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    seasonality = models.TextField(blank=True, null=True)
    fruiting_season_start = models.DateField(blank=True, null=True)
    fruiting_season_end = models.DateField(blank=True, null=True)
    fruit_bearing_position = models.TextField(blank=True, null=True)
    fruit_clustering_habit = models.TextField(blank=True, null=True)
    other_plant_characteristics = models.TextField(blank=True, null=True)

    pedicel_length_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_shape = models.TextField(blank=True, null=True)
    fruit_weight_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_length_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_width_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_thickness_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    skin_color = models.TextField(blank=True, null=True)
    skin_texture = models.TextField(blank=True, null=True)
    skin_thickness_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    flesh_thickness_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    flesh_weight_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    edible_portion_percent = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    flesh_color = models.TextField(blank=True, null=True)
    fruit_cross_section_shape = models.TextField(blank=True, null=True)
    taste = models.TextField(blank=True, null=True)
    flesh_aroma = models.TextField(blank=True, null=True)
    flesh_texture = models.TextField(blank=True, null=True)
    fruit_softness = models.TextField(blank=True, null=True)
    fruit_juiciness = models.TextField(blank=True, null=True)
    fruit_tss = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    seed_length_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    seed_width_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    seed_length_width_ratio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    number_of_seeds_per_fruit = models.IntegerField(blank=True, null=True)
    seed_shape = models.TextField(blank=True, null=True)
    hundred_seed_weight_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    other_characteristics = models.TextField(blank=True, null=True)
    evaluator = models.TextField(blank=True, null=True)

    photo = models.ImageField(upload_to='fruits_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Fruits Characteristics {self.id}"


class GardenspurgeCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='gardenspurge_characteristics')

    date_of_sowing = models.DateField(blank=True, null=True)
    date_of_planting_at_snap_solution = models.DateField(blank=True, null=True)
    number_of_days_to_germination = models.IntegerField(blank=True, null=True)
    stem_shape = models.TextField(blank=True, null=True)
    diameter_of_main_stem = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    color_of_stem = models.TextField(blank=True, null=True)
    stem_pubescence = models.TextField(blank=True, null=True)
    leaf_blade_margin = models.TextField(blank=True, null=True)
    leaf_shape = models.TextField(blank=True, null=True)
    leaf_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_width_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_color = models.TextField(blank=True, null=True)
    color_of_leaf_veins = models.TextField(blank=True, null=True)
    growth_habit = models.TextField(blank=True, null=True)
    growth_habit_of_stem = models.TextField(blank=True, null=True)
    plant_height_at_first_branching_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    number_of_branches_from_the_main_stem = models.IntegerField(blank=True, null=True)
    number_of_internodes = models.IntegerField(blank=True, null=True)
    presence_of_anthocyanin_on_the_leaves = models.TextField(blank=True, null=True)
    intensity_of_anthocyanin_pigmentation_on_the_leaf = models.TextField(blank=True, null=True)
    location_of_anthocyanin_pigmentation_on_the_leaf = models.TextField(blank=True, null=True)
    number_of_days_to_flowering = models.IntegerField(blank=True, null=True)
    diameter_of_umbel_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pedicel_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    number_of_days_first_harvest = models.IntegerField(blank=True, null=True)
    plant_height_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    photo = models.ImageField(upload_to='gardenspurge_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Gardenspurge Characteristics {self.id}"


class GingerCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='ginger_characteristics')

    days_to_emergence = models.IntegerField(blank=True, null=True)
    leaf_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_width_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_shape = models.TextField(blank=True, null=True)
    leaf_pubescence = models.TextField(blank=True, null=True)
    pseudostem_pubescence = models.TextField(blank=True, null=True)
    intensity_of_green_color_of_the_leaves = models.TextField(blank=True, null=True)
    number_of_leaves_per_plant = models.IntegerField(blank=True, null=True)
    days_to_harvest = models.IntegerField(blank=True, null=True)
    plant_height_at_harvest_m = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    presence_of_anthocyanin_in_one_third_portion_of_the_pseudostem = models.TextField(blank=True, null=True)
    pseudostem_diameter_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    bud_color = models.TextField(blank=True, null=True)
    number_of_rhizomes_per_plant = models.IntegerField(blank=True, null=True)
    weight_of_rhizomes_per_plant_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    number_of_internodes_in_the_rhizome = models.IntegerField(blank=True, null=True)
    rhizome_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    rhizome_diameter_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    rhizome_branching = models.TextField(blank=True, null=True)
    density_of_adventitious_root_on_the_rhizome = models.TextField(blank=True, null=True)
    rhizome_texture_skin = models.TextField(blank=True, null=True)
    rhizome_color_skin = models.TextField(blank=True, null=True)
    easiness_of_peeling_of_the_skin = models.TextField(blank=True, null=True)
    degree_of_fibrousness_of_the_rhizome = models.TextField(blank=True, null=True)

    photo = models.ImageField(upload_to='ginger_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Ginger Characteristics {self.id}"


class GotukolaCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='gotukola_characteristics')

    leaf_shape = models.TextField(blank=True, null=True)
    leaf_apex_shape = models.TextField(blank=True, null=True)
    leaf_base_shape = models.TextField(blank=True, null=True)
    leaf_base_lobing = models.TextField(blank=True, null=True)
    leaf_margin = models.TextField(blank=True, null=True)
    leaf_color = models.TextField(blank=True, null=True)
    leaf_blade_texture = models.TextField(blank=True, null=True)
    leaf_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_width_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_length_over_width_ratio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    petiole_color = models.TextField(blank=True, null=True)
    petiole_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stolon_color = models.TextField(blank=True, null=True)
    stolon_pubescence = models.TextField(blank=True, null=True)
    number_of_flowers_per_umbel = models.IntegerField(blank=True, null=True)
    petal_color = models.TextField(blank=True, null=True)
    bract_color = models.TextField(blank=True, null=True)
    peduncle_color = models.TextField(blank=True, null=True)
    fruit_shape = models.TextField(blank=True, null=True)
    fruit_color = models.TextField(blank=True, null=True)
    fruit_hairiness = models.TextField(blank=True, null=True)
    pedicel_length_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    seed_surface = models.TextField(blank=True, null=True)
    seed_length_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    seed_width_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    seed_shape = models.TextField(blank=True, null=True)
    hundred_seed_weight_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    photo = models.ImageField(upload_to='gotukola_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Gotukola Characteristics {self.id}"


class GuavaCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='guava_characteristics')

    tree_habit = models.TextField(blank=True, null=True)
    branching_habit = models.TextField(blank=True, null=True)
    branching_density = models.TextField(blank=True, null=True)
    branching_pattern = models.TextField(blank=True, null=True)
    arrangement = models.TextField(blank=True, null=True)
    shape = models.TextField(blank=True, null=True)
    apex_shape = models.TextField(blank=True, null=True)
    base_shape = models.TextField(blank=True, null=True)
    leaf_blade_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_blade_width_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_size_ratio_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_color = models.TextField(blank=True, null=True)
    petiole_length_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_upper_surface_pubescence_adaxial = models.TextField(blank=True, null=True)
    leaf_lower_surface_pubescence_abaxial = models.TextField(blank=True, null=True)
    stem_texture = models.TextField(blank=True, null=True)
    stem_color = models.TextField(blank=True, null=True)

    date_of_first_flowering = models.DateField(blank=True, null=True)
    inflorescence_color = models.TextField(blank=True, null=True)
    flower_density = models.TextField(blank=True, null=True)
    inflorescence_structure = models.TextField(blank=True, null=True)
    flower_clustering_habit = models.TextField(blank=True, null=True)
    number_of_years_to_first_fruiting_after_planting = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    number_of_years_from_flowering_to_maturity = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    fruit_clustering_habit = models.TextField(blank=True, null=True)
    fruit_shape = models.TextField(blank=True, null=True)
    peduncle_length_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_diameter_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_weight_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_surface_texture = models.TextField(blank=True, null=True)
    flesh_color = models.TextField(blank=True, null=True)
    fruit_rind_color = models.TextField(blank=True, null=True)
    number_of_locules = models.IntegerField(blank=True, null=True)
    seed_cavity_diameter_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    flesh_thickness_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    flesh_texture = models.TextField(blank=True, null=True)
    flesh_taste = models.TextField(blank=True, null=True)
    total_soluble_solids_percent_brix = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    seed_color = models.TextField(blank=True, null=True)
    seed_shape = models.TextField(blank=True, null=True)
    seed_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    seed_width = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    hundred_seed_weight_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    photo = models.ImageField(upload_to='guava_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Guava Characteristics {self.id}"


class HyacinthbeanCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='hyacinthbean_characteristics')

    plot_no = models.TextField(blank=True, null=True)
    sowing_date = models.DateField(blank=True, null=True)
    transplanting_date = models.DateField(blank=True, null=True)
    emerging_cotyledon_color = models.TextField(blank=True, null=True)
    hypocotyl_color = models.TextField(blank=True, null=True)
    hypocotyl_color_intensity = models.TextField(blank=True, null=True)
    hypocotyl_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    hypocotyl_pubescence = models.TextField(blank=True, null=True)
    days_to_emergence = models.IntegerField(blank=True, null=True)
    growth_habit = models.TextField(blank=True, null=True)
    clear_marking_along_veins = models.TextField(blank=True, null=True)
    vein_color_of_fully_developed_primary_leaves_on_inner_surface = models.TextField(blank=True, null=True)
    leaf_anthocyanin = models.TextField(blank=True, null=True)
    leaf_color_intensity = models.TextField(blank=True, null=True)
    leaf_hairiness = models.TextField(blank=True, null=True)
    leaf_persistence = models.TextField(blank=True, null=True)
    leaflet_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaflet_shape = models.TextField(blank=True, null=True)
    main_stem_pigmentation = models.TextField(blank=True, null=True)
    ramification_index_determinate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ramification_index_indeterminate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    branch_orientation = models.TextField(blank=True, null=True)
    plant_height = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    days_to_maturity = models.IntegerField(blank=True, null=True)
    number_of_nodes_on_main_stem_before_first_raceme = models.IntegerField(blank=True, null=True)
    days_to_flowering = models.IntegerField(blank=True, null=True)
    flower_bud_size = models.TextField(blank=True, null=True)
    color_of_flower_keel = models.TextField(blank=True, null=True)
    color_of_flower_standard = models.TextField(blank=True, null=True)
    color_of_flower_wings = models.TextField(blank=True, null=True)
    hairiness_of_standard_outer_face_of_freshly_opened_flower = models.TextField(blank=True, null=True)
    wing_opening = models.TextField(blank=True, null=True)
    number_of_nodes_per_raceme = models.IntegerField(blank=True, null=True)
    raceme_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    raceme_position = models.TextField(blank=True, null=True)
    duration_of_flowering = models.TextField(blank=True, null=True)
    pod_curvatures = models.TextField(blank=True, null=True)
    pod_pubescence = models.TextField(blank=True, null=True)
    pod_beak_shape = models.TextField(blank=True, null=True)
    position_of_pod_bearing_racemes = models.TextField(blank=True, null=True)
    orientation_of_pod_bearing_racemes = models.TextField(blank=True, null=True)
    pod_dehiscence_at_maturity = models.TextField(blank=True, null=True)
    days_to_first_pod_maturity = models.IntegerField(blank=True, null=True)
    pod_color_of_mature_pods = models.TextField(blank=True, null=True)
    pod_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pod_width_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    number_of_locules_per_pod = models.IntegerField(blank=True, null=True)
    number_of_seeds_per_pod = models.IntegerField(blank=True, null=True)
    seed_germination_within_pods = models.TextField(blank=True, null=True)
    splitting_of_seed_testa = models.TextField(blank=True, null=True)
    texture_of_seed_testa = models.TextField(blank=True, null=True)
    cotyledon_color_of_ripe_seeds = models.TextField(blank=True, null=True)
    background_color_the_lightest_color = models.TextField(blank=True, null=True)
    pattern_color = models.TextField(blank=True, null=True)
    shape_of_seed = models.TextField(blank=True, null=True)
    seed_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    seed_width_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    hundred_seed_weight_mg = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    photo = models.ImageField(upload_to='hyacinthbean_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Hyacinthbean Characteristics {self.id}"


class JatrophaCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='jatropha_characteristics')

    seedling = models.TextField(blank=True, null=True)
    tree_age = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tree_vigor = models.TextField(blank=True, null=True)
    tree_height_m = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tree_circumference_m = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    trunk_surface = models.TextField(blank=True, null=True)
    crown_diameter_m = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    crown_shape = models.TextField(blank=True, null=True)
    tree_growth_habit = models.TextField(blank=True, null=True)
    branching_density = models.TextField(blank=True, null=True)
    branching_pattern = models.TextField(blank=True, null=True)
    main_stem_pubescence = models.TextField(blank=True, null=True)
    main_stem_color = models.TextField(blank=True, null=True)
    primary_branch_color = models.TextField(blank=True, null=True)
    number_of_branches = models.IntegerField(blank=True, null=True)
    length_of_fruiting_branch = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    trunk_peeling = models.TextField(blank=True, null=True)
    leaf_position = models.TextField(blank=True, null=True)
    immature_leaf_color = models.TextField(blank=True, null=True)
    presence_of_axillary_leaves = models.TextField(blank=True, null=True)
    mature_leaf_color = models.TextField(blank=True, null=True)
    leaf_blade_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_blade_width_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_petiole_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_shape = models.TextField(blank=True, null=True)
    leaf_apex_shape = models.TextField(blank=True, null=True)
    leaf_base_shape = models.TextField(blank=True, null=True)
    leaf_blade_margin = models.TextField(blank=True, null=True)
    number_of_lobes = models.IntegerField(blank=True, null=True)
    leaf_adaxial_upper_surface_pubescence = models.TextField(blank=True, null=True)
    leaf_abaxial_upper_surface_pubescence = models.TextField(blank=True, null=True)
    leaf_midrib_pubescence = models.TextField(blank=True, null=True)
    petiole_pubescence = models.TextField(blank=True, null=True)
    petiole_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_petiole_color = models.TextField(blank=True, null=True)
    angle_of_petiole = models.TextField(blank=True, null=True)
    number_of_days_to_flowering = models.IntegerField(blank=True, null=True)
    flower_color = models.TextField(blank=True, null=True)
    presence_of_secondary_infloresence = models.TextField(blank=True, null=True)
    types_of_flowers_in_the_infloresence = models.TextField(blank=True, null=True)
    position_of_the_first_inflorescence = models.TextField(blank=True, null=True)
    presence_of_secondary_inflorescence = models.TextField(blank=True, null=True)
    date_of_occurrence_of_the_secondary_inflorescence = models.DateField(blank=True, null=True)
    number_clusters_per_branch = models.IntegerField(blank=True, null=True)
    cluster_peduncle_pubescence = models.TextField(blank=True, null=True)
    number_of_fruits_per_cluster = models.IntegerField(blank=True, null=True)
    cluster_peduncle_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    length_of_inflorescence_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    width_of_inflorescence_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    abundance_of_flowers_in_the_infloresence = models.TextField(blank=True, null=True)
    flower_pubescence = models.TextField(blank=True, null=True)
    position_of_petals = models.TextField(blank=True, null=True)
    number_of_sepals = models.IntegerField(blank=True, null=True)
    number_of_months_to_first_fruiting_after_planting_months = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    number_of_days_from_flowering_to_fruit_maturity_days = models.IntegerField(blank=True, null=True)
    duration_of_fruiting_months = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_ripening = models.TextField(blank=True, null=True)
    fruit_bearing_habit = models.TextField(blank=True, null=True)
    number_of_fruits_per_cluster_or_inflorescence = models.IntegerField(blank=True, null=True)
    fruit_shape = models.TextField(blank=True, null=True)
    immature_fruit_color = models.TextField(blank=True, null=True)
    mature_fruit_color = models.TextField(blank=True, null=True)
    fruit_splitting = models.TextField(blank=True, null=True)
    fruit_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_diameter_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    peduncle_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_weight_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    number_of_locules_per_fruit = models.IntegerField(blank=True, null=True)
    presence_of_fruit_pubescence = models.TextField(blank=True, null=True)
    fruit_pubescence = models.TextField(blank=True, null=True)
    pubescence_density = models.TextField(blank=True, null=True)
    skin_thickness_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    skin_weight_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    seed_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    seed_width_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    seed_weight_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    seed_shape = models.TextField(blank=True, null=True)
    seed_coat_color = models.TextField(blank=True, null=True)
    seed_coat_color_intensity = models.TextField(blank=True, null=True)
    seed_coat_thickness_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    adherence_of_seed_coat_to_seed = models.TextField(blank=True, null=True)

    photo = models.ImageField(upload_to='jatropha_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Jatropha Characteristics {self.id}"


class LagundiCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='lagundi_characteristics')

    personnel = models.TextField(blank=True, null=True)
    plant_growth_habit = models.TextField(blank=True, null=True)
    plant_height_m = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    plant_span_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stem_diameter_at_base_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    branching_habit = models.TextField(blank=True, null=True)
    leaf_growth_habit = models.TextField(blank=True, null=True)
    leaf_base_lobing = models.TextField(blank=True, null=True)
    leaflet_shape = models.TextField(blank=True, null=True)
    leaflet_apex_shape = models.TextField(blank=True, null=True)
    leaflet_base_shape = models.TextField(blank=True, null=True)
    leaflet_margin = models.TextField(blank=True, null=True)
    leaflet_color = models.TextField(blank=True, null=True)
    leaf_pubescence = models.TextField(blank=True, null=True)
    presence_of_leaf_bloom = models.TextField(blank=True, null=True)
    central_leaflet_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    central_leaflet_width = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    photo = models.ImageField(upload_to='lagundi_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Lagundi Characteristics {self.id}"


class LimabeanCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='limabean_characteristics')

    date_planted = models.DateField(blank=True, null=True)
    days_to_emergence = models.IntegerField(blank=True, null=True)
    emerging_cotyledon_colour = models.TextField(blank=True, null=True)
    hypocotyl_colour = models.TextField(blank=True, null=True)
    growth_pattern = models.TextField(blank=True, null=True)
    plant_height_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    branch_orientation = models.TextField(blank=True, null=True)
    ramification_index_determinate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ramification_index_indeterminate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaflet_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaflet_width_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaflet_shape = models.TextField(blank=True, null=True)
    leaf_anthocyanin = models.TextField(blank=True, null=True)
    leaf_colour = models.TextField(blank=True, null=True)
    leaf_hairiness_density = models.TextField(blank=True, null=True)
    main_stem_pigmentation = models.TextField(blank=True, null=True)
    clear_marking_along_veins_of_fully_developed_primary_leaves = models.TextField(blank=True, null=True)
    vein_color_of_fully_developed_primary_leaves_on_inner_face = models.TextField(blank=True, null=True)
    number_of_nodes_on_main_stem_from_the_base_to_the_first = models.IntegerField(blank=True, null=True)
    days_to_flowering = models.IntegerField(blank=True, null=True)
    color_of_flower_keel = models.TextField(blank=True, null=True)
    color_of_flower_standard = models.TextField(blank=True, null=True)
    colour_of_flower_wings = models.TextField(blank=True, null=True)
    flower_bud_size = models.TextField(blank=True, null=True)
    hairiness_of_flower = models.TextField(blank=True, null=True)
    wing_opening = models.TextField(blank=True, null=True)
    number_of_nodes_per_raceme = models.IntegerField(blank=True, null=True)
    raceme_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    raceme_position = models.TextField(blank=True, null=True)
    duration_of_flowering = models.TextField(blank=True, null=True)
    pod_curvature_of_fully_expanded_immature_pod = models.TextField(blank=True, null=True)
    pod_pubescence = models.TextField(blank=True, null=True)
    pod_beak_shape = models.TextField(blank=True, null=True)
    position_of_pod_bearing_racemes = models.TextField(blank=True, null=True)
    orientations_of_pod_bearing_raceme_at_maturity = models.TextField(blank=True, null=True)
    days_to_first_mature_pods = models.IntegerField(blank=True, null=True)
    mature_pod_colour = models.TextField(blank=True, null=True)
    pod_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pod_width_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    number_of_locules_per_pod = models.IntegerField(blank=True, null=True)
    pod_dehiscence = models.TextField(blank=True, null=True)
    background_colour = models.TextField(blank=True, null=True)
    pattern_colour = models.TextField(blank=True, null=True)
    secondary_pattern_colour = models.TextField(blank=True, null=True)
    seed_coat_pattern = models.TextField(blank=True, null=True)
    shape_of_seed = models.TextField(blank=True, null=True)
    seed_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    seed_width = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    seed_thickness = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    number_of_pods_per_plant = models.IntegerField(blank=True, null=True)
    yield_per_plant_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ten_pod_weight_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    number_of_seeds_per_pod = models.IntegerField(blank=True, null=True)
    percentage_of_first_harvest = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    hundred_seed_weight_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    photo = models.ImageField(upload_to='limabean_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Limabean Characteristics {self.id}"


class LuffaCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='luffa_characteristics')

    plot_no = models.TextField(blank=True, null=True)
    sowing_date = models.DateField(blank=True, null=True)
    cotyledon_size = models.TextField(blank=True, null=True)
    cotyledon_color = models.TextField(blank=True, null=True)
    number_of_days_from_sowing_to_emergence = models.IntegerField(blank=True, null=True)
    internode_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stem_shape = models.TextField(blank=True, null=True)
    tendrils = models.TextField(blank=True, null=True)
    leaf_shape = models.TextField(blank=True, null=True)
    leaf_size = models.TextField(blank=True, null=True)
    color_of_leaf_spots_or_checks = models.TextField(blank=True, null=True)
    leaf_margin = models.TextField(blank=True, null=True)
    leaf_lobes = models.TextField(blank=True, null=True)
    leaf_pubescence_dorsal_surface = models.TextField(blank=True, null=True)
    leaf_pubescence_ventral_side = models.TextField(blank=True, null=True)
    plant_growth_habit = models.TextField(blank=True, null=True)
    time_of_maturity = models.TextField(blank=True, null=True)
    days_to_flowering = models.IntegerField(blank=True, null=True)
    flower_color = models.TextField(blank=True, null=True)
    flower_seed = models.TextField(blank=True, null=True)
    sex_type = models.TextField(blank=True, null=True)
    peduncle_transectional_shape = models.TextField(blank=True, null=True)
    peduncle_attachment = models.TextField(blank=True, null=True)
    peduncle_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    peduncle_separation_from_fruit = models.TextField(blank=True, null=True)
    stem_end_fruit_shape = models.TextField(blank=True, null=True)
    blossom_end_fruit_shape = models.TextField(blank=True, null=True)
    fruit_shape = models.TextField(blank=True, null=True)
    fruit_ribs = models.TextField(blank=True, null=True)
    fruit_rib_shape = models.TextField(blank=True, null=True)
    fruit_size_variability = models.TextField(blank=True, null=True)
    predominant_fruit_skin_color_at_maturity = models.TextField(blank=True, null=True)
    fruit_skin_color_intensity = models.TextField(blank=True, null=True)
    fruit_skin_texture = models.TextField(blank=True, null=True)
    fruit_skin_texture_intensity = models.TextField(blank=True, null=True)
    fruit_lustre = models.TextField(blank=True, null=True)
    fruit_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_width_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_weight_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_skin_thickness_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    flesh_thickness_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cavity_diameter = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_skin_hardness = models.TextField(blank=True, null=True)
    flesh_color = models.TextField(blank=True, null=True)
    flesh_moisture = models.TextField(blank=True, null=True)
    flesh_texture = models.TextField(blank=True, null=True)
    amount_of_placental_tissue = models.TextField(blank=True, null=True)
    ease_of_seed_and_placenta_separation_from_flesh = models.TextField(blank=True, null=True)
    flesh_flavor = models.TextField(blank=True, null=True)
    number_of_seeds_per_fruit = models.IntegerField(blank=True, null=True)
    seed_surface = models.TextField(blank=True, null=True)
    seed_surface_lustre = models.TextField(blank=True, null=True)
    seed_color = models.TextField(blank=True, null=True)
    hundred_seed_weight_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    photo = models.ImageField(upload_to='luffa_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Luffa Characteristics {self.id}"


class MalunggayCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='malunggay_characteristics')

    tree_shape_or_habit = models.TextField(blank=True, null=True)
    tree_nature = models.TextField(blank=True, null=True)
    plant_height_aboveground_m = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stem_diameter_at_the_base_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    branching_habit = models.TextField(blank=True, null=True)
    bark_color_of_mature_tree = models.TextField(blank=True, null=True)
    number_of_branchlets_per_node = models.IntegerField(blank=True, null=True)
    foliage_density = models.TextField(blank=True, null=True)
    leaflet_shape = models.TextField(blank=True, null=True)
    leaflet_apex_shape = models.TextField(blank=True, null=True)
    leaf_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_width_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_length_width_ratio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    date_of_first_flowering = models.DateField(blank=True, null=True)
    number_of_inflorescence_per_branchlet = models.IntegerField(blank=True, null=True)
    flower_position_on_branchlet = models.TextField(blank=True, null=True)
    nature_of_calyx = models.TextField(blank=True, null=True)
    calyx_color = models.TextField(blank=True, null=True)
    nature_of_corolla = models.TextField(blank=True, null=True)
    corolla_color = models.TextField(blank=True, null=True)
    pink_spots_in_corolla = models.TextField(blank=True, null=True)
    date_of_first_fruit_maturity = models.DateField(blank=True, null=True)
    fruit_maturity = models.TextField(blank=True, null=True)
    fruit_orientation = models.TextField(blank=True, null=True)
    pulp_color = models.TextField(blank=True, null=True)
    number_of_fruits_per_tree = models.IntegerField(blank=True, null=True)
    fruit_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_girth_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_weight_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    number_of_longitudinal_ridges_per_fruit = models.IntegerField(blank=True, null=True)
    seed_color = models.TextField(blank=True, null=True)
    seed_shape = models.TextField(blank=True, null=True)
    number_of_seeds_per_fruit = models.IntegerField(blank=True, null=True)
    seed_diameter_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    hundred_seed_weight_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    photo = models.ImageField(upload_to='malunggay_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Malunggay Characteristics {self.id}"


class MangosteenCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='mangosteen_characteristics')

    tree_type = models.TextField(blank=True, null=True)
    tree_height_m = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    trunk_height_m = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    trunk_circumference_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    trunk_surface = models.TextField(blank=True, null=True)
    crown_shape = models.TextField(blank=True, null=True)
    tree_growth_habit = models.TextField(blank=True, null=True)
    branching_density = models.TextField(blank=True, null=True)
    branching_pattern = models.TextField(blank=True, null=True)
    young_shoot_pubescence = models.TextField(blank=True, null=True)
    young_leaf_color = models.TextField(blank=True, null=True)
    mature_leaf_color = models.TextField(blank=True, null=True)
    leaf_density = models.TextField(blank=True, null=True)
    arrangement_of_leaves = models.TextField(blank=True, null=True)
    petiole_length_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    petiole_width_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_blade_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_blade_width_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_blade_shape = models.TextField(blank=True, null=True)
    leaf_apex_shape = models.TextField(blank=True, null=True)
    leaf_base_shape = models.TextField(blank=True, null=True)
    leaf_blade_margin = models.TextField(blank=True, null=True)
    leaf_upper_surface_pubescence = models.TextField(blank=True, null=True)
    leaf_lower_surface_pubescence = models.TextField(blank=True, null=True)
    leaf_midrib_appearance = models.TextField(blank=True, null=True)
    leaf_venation_appearance = models.TextField(blank=True, null=True)
    flower_clustering_habit = models.TextField(blank=True, null=True)
    number_of_stigma_lobes = models.IntegerField(blank=True, null=True)
    number_of_sepals = models.IntegerField(blank=True, null=True)
    sepal_color = models.TextField(blank=True, null=True)
    petal_color = models.TextField(blank=True, null=True)
    flower_size = models.TextField(blank=True, null=True)
    position_of_flowers = models.TextField(blank=True, null=True)
    fruit_clustering_habit = models.TextField(blank=True, null=True)
    fruit_shape = models.TextField(blank=True, null=True)
    stigma_lobe_persistence = models.TextField(blank=True, null=True)
    persistent_stigma_lobe_thickness = models.TextField(blank=True, null=True)
    blotches_sorrounding_stigma_lobe = models.TextField(blank=True, null=True)
    color_of_stigma_lobe = models.TextField(blank=True, null=True)
    pedicel_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pedicel_attachment = models.TextField(blank=True, null=True)
    pedicel_color = models.TextField(blank=True, null=True)
    fruit_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_diameter_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_weight_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_size = models.TextField(blank=True, null=True)
    fruit_skin_thickness = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    mature_fruit_color = models.TextField(blank=True, null=True)
    aril_quality = models.TextField(blank=True, null=True)
    aril_texture = models.TextField(blank=True, null=True)
    aril_flavor = models.TextField(blank=True, null=True)
    aril_taste = models.TextField(blank=True, null=True)
    aril_color = models.TextField(blank=True, null=True)
    number_of_arils_per_fruit = models.IntegerField(blank=True, null=True)
    seed_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    seed_width_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    seed_thickness_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    number_of_mature_seeds_per_fruit = models.IntegerField(blank=True, null=True)
    seed_shape = models.TextField(blank=True, null=True)
    seed_coat_color = models.TextField(blank=True, null=True)

    photo = models.ImageField(upload_to='mangosteen_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Mangosteen Characteristics {self.id}"


class MungbeanCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='mungbean_characteristics')

    sowing_date = models.DateField(blank=True, null=True)
    days_to_emergence = models.IntegerField(blank=True, null=True)
    hypocotyl_color = models.TextField(blank=True, null=True)
    seedling_vigour = models.TextField(blank=True, null=True)
    growth_habit = models.TextField(blank=True, null=True)
    growth_pattern = models.TextField(blank=True, null=True)
    twining_tendency = models.TextField(blank=True, null=True)
    primary_leaf_shape = models.TextField(blank=True, null=True)
    primary_leaf_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    prim_lf_lt_3_4_wap = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    prim_lf_wdt_4_5_wap_actual = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    prim_lf_wdt_4_5_wap_range = models.TextField(blank=True, null=True)
    leaf_color_intensity = models.TextField(blank=True, null=True)
    leafiness = models.TextField(blank=True, null=True)
    terminal_leaflet_shape = models.TextField(blank=True, null=True)
    terminal_leaflet_length_actual = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    terminal_leaflet_length_range = models.TextField(blank=True, null=True)
    terminal_leaflet_width_actual = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    terminal_leaflet_width_range = models.TextField(blank=True, null=True)
    leaf_pubescence = models.TextField(blank=True, null=True)
    petiole_length_actual = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    petiole_length_range = models.TextField(blank=True, null=True)
    petiole_color = models.TextField(blank=True, null=True)
    color_of_petiole_or_leaf_blade_joint = models.TextField(blank=True, null=True)
    color_of_basal_petioles = models.TextField(blank=True, null=True)
    number_of_primary_branches = models.IntegerField(blank=True, null=True)
    branch_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_senescence = models.TextField(blank=True, null=True)
    branching_pattern = models.TextField(blank=True, null=True)
    days_to_flowering = models.IntegerField(blank=True, null=True)
    first_pod_bearing_node = models.IntegerField(blank=True, null=True)
    calyx_color = models.TextField(blank=True, null=True)
    flower_standard_color = models.TextField(blank=True, null=True)
    flower_wing_color = models.TextField(blank=True, null=True)
    flower_keel_color = models.TextField(blank=True, null=True)
    flowering_period = models.TextField(blank=True, null=True)
    pod_setting_capacity_percent = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    raceme_position = models.TextField(blank=True, null=True)
    peduncle_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    number_of_pod_bearing_peduncles = models.IntegerField(blank=True, null=True)
    pod_attachment_to_peduncle = models.TextField(blank=True, null=True)
    immature_pod_color = models.TextField(blank=True, null=True)
    color_of_ventral_structure_of_immature_pod = models.TextField(blank=True, null=True)
    days_to_first_mature_pods = models.IntegerField(blank=True, null=True)
    mature_pod_color = models.TextField(blank=True, null=True)
    pod_pubescence = models.TextField(blank=True, null=True)
    pod_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pod_shattering_in_the_field = models.TextField(blank=True, null=True)
    lodging = models.TextField(blank=True, null=True)
    pod_cross_section_mature_pod = models.TextField(blank=True, null=True)
    pod_beak_shape = models.TextField(blank=True, null=True)
    constriction_of_pod = models.TextField(blank=True, null=True)
    pod_curvature = models.TextField(blank=True, null=True)
    yield_per_plant_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    percentage_of_first_harvest = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    number_of_seeds_per_pod = models.IntegerField(blank=True, null=True)
    seed_shape = models.TextField(blank=True, null=True)
    seed_color = models.TextField(blank=True, null=True)
    mottling_on_seed = models.TextField(blank=True, null=True)
    luster_on_seed_surface = models.TextField(blank=True, null=True)
    hilum = models.TextField(blank=True, null=True)
    ten_pod_weight_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    hundred_seed_weight_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    photo = models.ImageField(upload_to='mungbean_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Mungbean Characteristics {self.id}"


class PeanutCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='peanut_characteristics')

    sowing_date = models.DateField(blank=True, null=True)
    days_to_emergence = models.IntegerField(blank=True, null=True)
    plant_growth_habit_pgh = models.TextField(blank=True, null=True)
    branching_pattern = models.TextField(blank=True, null=True)
    stem_pigmentation = models.TextField(blank=True, null=True)
    stem_hairiness = models.TextField(blank=True, null=True)
    lateral_branch_habit = models.TextField(blank=True, null=True)
    main_stem_growth_habit_msgh = models.TextField(blank=True, null=True)
    side_branches_growth_habit_sbgh = models.TextField(blank=True, null=True)
    plant_branching_as_for_1_pbh = models.TextField(blank=True, null=True)
    length_of_reproductive_branch_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    time_of_maturity_for_curing = models.TextField(blank=True, null=True)
    leaflet_size = models.TextField(blank=True, null=True)
    leaflet_color = models.TextField(blank=True, null=True)
    leaf_length_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaflet_width_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaflet_shape = models.TextField(blank=True, null=True)
    hairiness_of_young_leaflets = models.TextField(blank=True, null=True)
    hairiness_of_mature_leaflets = models.TextField(blank=True, null=True)
    days_to_50_percent_flowering = models.IntegerField(blank=True, null=True)
    number_of_flowers_per_inflorescence = models.IntegerField(blank=True, null=True)
    peg_color = models.TextField(blank=True, null=True)
    flowering_general_pattern = models.TextField(blank=True, null=True)
    flowering_pattern_of_main_stem = models.TextField(blank=True, null=True)
    standard_petal_color = models.TextField(blank=True, null=True)
    standard_petal_markings = models.TextField(blank=True, null=True)
    days_to_maturity = models.IntegerField(blank=True, null=True)
    plant_height_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pod_constrictions = models.TextField(blank=True, null=True)
    pod_surface_texture = models.TextField(blank=True, null=True)
    pod_reticulation = models.TextField(blank=True, null=True)
    number_of_kernels = models.IntegerField(blank=True, null=True)
    pod_prominence_of_beak = models.TextField(blank=True, null=True)
    pod_shape_of_beak = models.TextField(blank=True, null=True)
    pod_length_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pod_width_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    color_of_uncured_mature_testa = models.TextField(blank=True, null=True)
    color_of_monochromatic_uncured_mature_testa = models.TextField(blank=True, null=True)
    kernel_shape = models.TextField(blank=True, null=True)
    kernel_size = models.TextField(blank=True, null=True)
    number_of_seeds_per_pod = models.IntegerField(blank=True, null=True)
    seed_number_of_colors = models.TextField(blank=True, null=True)
    primary_dried_seed_color = models.TextField(blank=True, null=True)
    secondary_dried_seed_color = models.TextField(blank=True, null=True)
    seed_length_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    seed_width_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    number_of_pods_per_plant = models.IntegerField(blank=True, null=True)
    yield_per_plant_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    weight_of_ten_pods_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    percentage_of_first_harvest_over_total_harvest_percent = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    hundred_seed_weight_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    photo = models.ImageField(upload_to='peanut_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Peanut Characteristics {self.id}"


class PepperCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='pepper_characteristics')

    plot_no = models.TextField(blank=True, null=True)
    sowing_date = models.DateField(blank=True, null=True)
    transplanting_date = models.DateField(blank=True, null=True)
    hypocotyl_color = models.TextField(blank=True, null=True)
    hypocotyl_pubescence = models.TextField(blank=True, null=True)
    cotyledonous_leaf_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cotyledonous_leaf_width = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cotyledonous_leaf_shape = models.TextField(blank=True, null=True)
    cotyledonous_leaf_color = models.TextField(blank=True, null=True)
    stem_color = models.TextField(blank=True, null=True)
    nodal_anthocyanin = models.TextField(blank=True, null=True)
    stem_shape = models.TextField(blank=True, null=True)
    stem_pubescence = models.TextField(blank=True, null=True)
    hairiness_of_nodes = models.TextField(blank=True, null=True)
    plant_height = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    plant_growth_habit = models.TextField(blank=True, null=True)
    plant_canopy_width = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stem_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stem_diameter = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    branching_habit = models.TextField(blank=True, null=True)
    shortened_internode_upper_part = models.TextField(blank=True, null=True)
    number_of_internodes = models.IntegerField(blank=True, null=True)
    length_of_internodes = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_profile_in_cross_section = models.TextField(blank=True, null=True)
    tillering = models.TextField(blank=True, null=True)
    leaf_density = models.TextField(blank=True, null=True)
    leaf_color = models.TextField(blank=True, null=True)
    leaf_intensity_of_green_color = models.TextField(blank=True, null=True)
    leaf_shape = models.TextField(blank=True, null=True)
    lamina_margin = models.TextField(blank=True, null=True)
    leaf_pubescence = models.TextField(blank=True, null=True)
    leaf_blistering = models.TextField(blank=True, null=True)
    mature_leaf_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    mature_leaf_width = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_glossiness = models.TextField(blank=True, null=True)
    pedicel_attitude = models.TextField(blank=True, null=True)
    number_of_pedicel_per_axil = models.IntegerField(blank=True, null=True)
    pedicel_position_at_anthesis = models.TextField(blank=True, null=True)
    angle_between_flower_and_pedicel = models.TextField(blank=True, null=True)
    corolla_color = models.TextField(blank=True, null=True)
    calyx_margin_shape = models.TextField(blank=True, null=True)
    annular_constriction_at_junction_of_calyx_and_penducle = models.TextField(blank=True, null=True)
    corrolla_spot = models.TextField(blank=True, null=True)
    anther_color = models.TextField(blank=True, null=True)
    filament_color = models.TextField(blank=True, null=True)
    stigma_position = models.TextField(blank=True, null=True)
    days_to_flower = models.IntegerField(blank=True, null=True)
    corolla_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_width = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_wall_thickness = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_pedicel_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    number_of_locules = models.IntegerField(blank=True, null=True)
    soluble_solids = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    calyx_aspect = models.TextField(blank=True, null=True)
    fruit_position = models.TextField(blank=True, null=True)
    fruit_color_at_immature_stage = models.TextField(blank=True, null=True)
    fruit_color_intensity_at_immature_stage = models.TextField(blank=True, null=True)
    fruit_color_at_intermediate_stage = models.TextField(blank=True, null=True)
    fruit_color_at_mature_stage = models.TextField(blank=True, null=True)
    fruit_color_intensity_at_mature_stage = models.TextField(blank=True, null=True)
    fruit_shape = models.TextField(blank=True, null=True)
    fruit_shape_at_peduncle_attachment = models.TextField(blank=True, null=True)
    neck_at_base_of_fruit = models.TextField(blank=True, null=True)
    fruit_shape_at_blossom_end = models.TextField(blank=True, null=True)
    fruit_cross_sectional_corrugation = models.TextField(blank=True, null=True)
    fruit_persistence = models.TextField(blank=True, null=True)
    duration_of_fruiting = models.TextField(blank=True, null=True)
    fruit_set = models.TextField(blank=True, null=True)
    varietal_mixture_condition = models.TextField(blank=True, null=True)
    anthocyanin_spots_in_unripe_stage = models.TextField(blank=True, null=True)
    seed_color = models.TextField(blank=True, null=True)
    seed_surface = models.TextField(blank=True, null=True)
    seed_diameter = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    number_of_seeds_per_fruit = models.IntegerField(blank=True, null=True)
    thousand_seed_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    photo = models.ImageField(upload_to='pepper_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Pepper Characteristics {self.id}"


class PigeonpeaCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='pigeonpea_characteristics')

    sowing_date = models.DateField(blank=True, null=True)
    transplanting_date = models.DateField(blank=True, null=True)
    hypocotyl_color = models.TextField(blank=True, null=True)
    hypocotyl_color_intensity = models.TextField(blank=True, null=True)
    cotyledonous_leaf_length_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cotyledonous_leaf_width_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cotyledonous_leaf_shape = models.TextField(blank=True, null=True)
    cotyledonous_leaf_color = models.TextField(blank=True, null=True)
    hypocotyl_pubescence = models.TextField(blank=True, null=True)
    days_to_emergence = models.IntegerField(blank=True, null=True)
    plant_growth_habit = models.TextField(blank=True, null=True)
    growth_pattern = models.TextField(blank=True, null=True)
    attachment_of_primary_leaves = models.TextField(blank=True, null=True)
    primary_leaf_shape = models.TextField(blank=True, null=True)
    leaf_color = models.TextField(blank=True, null=True)
    leaf_pubescence = models.TextField(blank=True, null=True)
    terminal_leaflet_shape = models.TextField(blank=True, null=True)
    terminal_leaflet_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leafiness = models.TextField(blank=True, null=True)
    petiole_color = models.TextField(blank=True, null=True)
    stem_color = models.TextField(blank=True, null=True)
    days_to_75_percent_maturity = models.IntegerField(blank=True, null=True)
    plant_height_at_maturity_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    branching_orientation = models.TextField(blank=True, null=True)
    diameter_of_canopy_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    days_to_50_percent_flowering = models.IntegerField(blank=True, null=True)
    raceme_position = models.TextField(blank=True, null=True)
    raceme_number = models.IntegerField(blank=True, null=True)
    flowering_pattern = models.TextField(blank=True, null=True)
    flower_main_color = models.TextField(blank=True, null=True)
    second_flower_color = models.TextField(blank=True, null=True)
    pattern_of_streaks = models.TextField(blank=True, null=True)
    pod_bearing_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pod_color_at_immature_stage = models.TextField(blank=True, null=True)
    attachment_of_mature_pod_to_peduncle = models.TextField(blank=True, null=True)
    pod_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pod_pubescence = models.TextField(blank=True, null=True)
    constriction_of_pod_between_seeds = models.TextField(blank=True, null=True)
    pod_curvature = models.TextField(blank=True, null=True)
    pod_beak_shape = models.TextField(blank=True, null=True)
    dry_pod_color = models.TextField(blank=True, null=True)
    seed_color_pattern = models.TextField(blank=True, null=True)
    seed_main_color = models.TextField(blank=True, null=True)
    seed_second_color = models.TextField(blank=True, null=True)
    mature_seed_color = models.TextField(blank=True, null=True)
    eye_color = models.TextField(blank=True, null=True)
    eye_size = models.TextField(blank=True, null=True)
    seed_shape = models.TextField(blank=True, null=True)
    hilum = models.TextField(blank=True, null=True)
    seed_number_per_pod = models.IntegerField(blank=True, null=True)
    hundred_seed_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    photo = models.ImageField(upload_to='pigeonpea_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Pigeonpea Characteristics {self.id}"


class PolesitaoCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='polesitao_characteristics')

    plot_no = models.TextField(blank=True, null=True)
    date_planted = models.DateField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    days_to_emergence = models.IntegerField(blank=True, null=True)
    anthocyanin_coloration_of_hypocotyls = models.TextField(blank=True, null=True)
    hypocotyl_color = models.TextField(blank=True, null=True)
    hypocotyl_color_intensity = models.TextField(blank=True, null=True)
    hypocotyl_pubescence = models.TextField(blank=True, null=True)
    hypocotyl_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cotyledonous_leaf_color = models.TextField(blank=True, null=True)
    cotyledonous_leaf_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cotyledonous_leaf_width = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    growth_habit = models.TextField(blank=True, null=True)
    ramification_index = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    branch_orientation = models.TextField(blank=True, null=True)
    internode_color = models.TextField(blank=True, null=True)
    leaf_shape = models.TextField(blank=True, null=True)
    leaf_color = models.TextField(blank=True, null=True)
    terminal_leaflet_length_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    terminal_leaflet_width_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_pubescence = models.TextField(blank=True, null=True)
    petiole_color = models.TextField(blank=True, null=True)
    basal_petiole_color = models.TextField(blank=True, null=True)
    petiole_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    shape_of_leaf_apex = models.TextField(blank=True, null=True)
    shape_of_leaf_bases = models.TextField(blank=True, null=True)
    shape_of_leaf_margin = models.TextField(blank=True, null=True)
    venation_of_the_leaf_blade = models.TextField(blank=True, null=True)
    days_to_flowering = models.IntegerField(blank=True, null=True)
    number_of_nodes_on_main_stem_before_first_raceme = models.IntegerField(blank=True, null=True)
    color_of_flower_keel = models.TextField(blank=True, null=True)
    color_of_flower_standard = models.TextField(blank=True, null=True)
    color_of_flower_wings = models.TextField(blank=True, null=True)
    days_to_first_mature_pod = models.IntegerField(blank=True, null=True)
    immature_pod_pigmentation = models.TextField(blank=True, null=True)
    immature_pod_color = models.TextField(blank=True, null=True)
    mature_pod_color_dry_pod = models.TextField(blank=True, null=True)
    pod_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pod_width = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pod_beak_position = models.TextField(blank=True, null=True)
    pod_beak_orientation = models.TextField(blank=True, null=True)
    pod_curvature = models.TextField(blank=True, null=True)
    pericarp_thickness = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    number_of_locules_per_pod = models.IntegerField(blank=True, null=True)
    prominence_of_seed_locules = models.TextField(blank=True, null=True)
    pod_surface_texture = models.TextField(blank=True, null=True)
    pod_waxiness = models.TextField(blank=True, null=True)
    pod_cross_section = models.TextField(blank=True, null=True)
    number_of_seed_per_pod = models.IntegerField(blank=True, null=True)
    seed_shape = models.TextField(blank=True, null=True)
    seed_number_of_colors = models.TextField(blank=True, null=True)
    seed_main_color = models.TextField(blank=True, null=True)
    seed_predominant_secondary_color = models.TextField(blank=True, null=True)
    seed_distribution_of_secondary_color = models.TextField(blank=True, null=True)
    seed_coat_texture = models.TextField(blank=True, null=True)
    seed_coat_luster = models.TextField(blank=True, null=True)
    hilum_color_eye_color = models.TextField(blank=True, null=True)
    hilar_ring_color = models.TextField(blank=True, null=True)
    seed_veining = models.TextField(blank=True, null=True)
    seed_length_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    seed_width_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    hundred_seed_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    photo = models.ImageField(upload_to='polesitao_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Polesitao Characteristics {self.id}"


class RicebeanCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='ricebean_characteristics')

    plot_no = models.TextField(blank=True, null=True)
    sowing_date = models.DateField(blank=True, null=True)
    country_of_characterization = models.TextField(blank=True, null=True)
    site_research_institute = models.TextField(blank=True, null=True)
    name_of_person_in_charge_of_characterization = models.TextField(blank=True, null=True)
    harvest_date = models.DateField(blank=True, null=True)
    population_density = models.TextField(blank=True, null=True)
    days_to_emergence = models.IntegerField(blank=True, null=True)
    type_of_germination = models.TextField(blank=True, null=True)
    seedling_vigour = models.TextField(blank=True, null=True)
    hypocotyl_or_epicotyl_color = models.TextField(blank=True, null=True)
    growth_pattern = models.TextField(blank=True, null=True)
    twining_tendency = models.TextField(blank=True, null=True)
    life_span = models.TextField(blank=True, null=True)
    plant_height = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    attachment_of_primary_leaves = models.TextField(blank=True, null=True)
    terminal_leaflet_shape = models.TextField(blank=True, null=True)
    terminal_leaflet_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    terminal_leaflet_width_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_pubescence = models.TextField(blank=True, null=True)
    leaf_color = models.TextField(blank=True, null=True)
    petiole_color = models.TextField(blank=True, null=True)
    petiole_leaf_blade_joint = models.TextField(blank=True, null=True)
    color_of_basal_petiole = models.TextField(blank=True, null=True)
    petiole_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    color_at_leaf_axil = models.TextField(blank=True, null=True)
    terminal_petiolule_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stipule_size = models.TextField(blank=True, null=True)
    stipule_shape = models.TextField(blank=True, null=True)
    ligule = models.TextField(blank=True, null=True)
    leaf_senescence = models.TextField(blank=True, null=True)
    stem_color = models.TextField(blank=True, null=True)
    stem_thickness_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stem_pubescence = models.TextField(blank=True, null=True)
    stem_hair_color = models.TextField(blank=True, null=True)
    number_of_main_branches = models.IntegerField(blank=True, null=True)
    branch_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    branching_pattern = models.TextField(blank=True, null=True)
    lodging = models.TextField(blank=True, null=True)
    nodulation = models.TextField(blank=True, null=True)
    days_to_flowering = models.IntegerField(blank=True, null=True)
    photoperiodism_of_flowering = models.TextField(blank=True, null=True)
    first_pod_bearing_node = models.IntegerField(blank=True, null=True)
    size_of_bracteole = models.TextField(blank=True, null=True)
    hairiness_of_bracteole = models.TextField(blank=True, null=True)
    flower_bud_size = models.TextField(blank=True, null=True)
    calyx_color = models.TextField(blank=True, null=True)
    corolla_color = models.TextField(blank=True, null=True)
    color_of_flower_keel = models.TextField(blank=True, null=True)
    color_of_flower_standard = models.TextField(blank=True, null=True)
    hairiness_of_standard = models.TextField(blank=True, null=True)
    raceme_position = models.TextField(blank=True, null=True)
    number_of_flowers_per_raceme = models.IntegerField(blank=True, null=True)
    ovary_hairiness = models.TextField(blank=True, null=True)
    stigma_shape = models.TextField(blank=True, null=True)
    stigma_beard = models.TextField(blank=True, null=True)
    fruit_setting_capability = models.TextField(blank=True, null=True)
    number_of_branches = models.IntegerField(blank=True, null=True)
    length_of_branch = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    peduncle_color = models.TextField(blank=True, null=True)
    peduncle_pubescence = models.TextField(blank=True, null=True)
    peduncle_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    number_of_pod_bearing_peduncle = models.IntegerField(blank=True, null=True)
    number_of_pods_per_peduncle = models.IntegerField(blank=True, null=True)
    pod_color_at_immature_stage = models.TextField(blank=True, null=True)
    color_of_ventral_suture_of_immature_pod = models.TextField(blank=True, null=True)
    days_to_first_mature_pod = models.IntegerField(blank=True, null=True)
    days_to_50_percent_ripe_pods = models.IntegerField(blank=True, null=True)
    pod_color_at_mature_stage = models.TextField(blank=True, null=True)
    shape_of_ripe_pods = models.TextField(blank=True, null=True)
    attachment_of_mature_pod_to_peduncle = models.TextField(blank=True, null=True)
    pod_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pod_width = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pod_pubescence = models.TextField(blank=True, null=True)
    pod_shattering_in_the_field = models.TextField(blank=True, null=True)
    constriction_of_pod_between_seeds = models.TextField(blank=True, null=True)
    pod_filling = models.TextField(blank=True, null=True)
    pod_beak_shape = models.TextField(blank=True, null=True)
    pod_curvature = models.TextField(blank=True, null=True)
    ovules_per_pod = models.IntegerField(blank=True, null=True)
    number_of_locules_per_pod_ovule_attachment = models.TextField(blank=True, null=True)
    pod_suture_string = models.TextField(blank=True, null=True)
    pod_background_color = models.TextField(blank=True, null=True)
    number_of_seeds_per_pod = models.IntegerField(blank=True, null=True)
    seed_coat_pattern_mottling_on_seeds = models.TextField(blank=True, null=True)
    type_of_seed_coat_pattern = models.TextField(blank=True, null=True)
    darker_color_of_seed_coat_pattern = models.TextField(blank=True, null=True)
    luster_on_seed_surface = models.TextField(blank=True, null=True)
    seed_shape = models.TextField(blank=True, null=True)
    seed_shape_outline = models.TextField(blank=True, null=True)
    hilum_at_full_maturity = models.TextField(blank=True, null=True)
    seed_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    seed_width = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    seed_thickness = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    seed_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    photo = models.ImageField(upload_to='ricebean_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Ricebean Characteristics {self.id}"


class SabilaCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='sabila_characteristics')

    plant_height_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    number_of_suckers_per_plant_pcs = models.IntegerField(blank=True, null=True)
    spine_frequency_per_10_cm_length_of_leaf_pcs = models.IntegerField(blank=True, null=True)
    spine_base_color = models.TextField(blank=True, null=True)
    spine_tip_color = models.TextField(blank=True, null=True)
    spine_tip_nature = models.TextField(blank=True, null=True)
    intensity_of_green_color_in_leaf_adaxial = models.TextField(blank=True, null=True)
    intensity_of_green_color_in_leaf_abaxial = models.TextField(blank=True, null=True)
    leaf_spots_presence = models.TextField(blank=True, null=True)
    leaf_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_width_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_diameter_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_length_width_ratio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    date_of_first_flowering = models.DateField(blank=True, null=True)
    number_of_inflorescence_per_plant_pcs = models.IntegerField(blank=True, null=True)
    inflorescence_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    number_of_flowers_per_inflorescence_pcs = models.IntegerField(blank=True, null=True)
    flower_color = models.TextField(blank=True, null=True)
    flower_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_setting = models.TextField(blank=True, null=True)
    number_of_fruits_per_inflorescence_pcs = models.IntegerField(blank=True, null=True)
    immature_fruit_color = models.TextField(blank=True, null=True)
    mature_fruit_color = models.TextField(blank=True, null=True)
    number_of_seeds_per_fruit_pcs = models.IntegerField(blank=True, null=True)

    photo = models.ImageField(upload_to='sabila_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Sabila Characteristics {self.id}"


class SambongCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='sambong_characteristics')

    plant_height_aboveground_m = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stem_hairiness = models.TextField(blank=True, null=True)
    internode_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stem_diameter_at_the_base_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_shape = models.TextField(blank=True, null=True)
    leaf_apex = models.TextField(blank=True, null=True)
    leaf_base = models.TextField(blank=True, null=True)
    leaf_margin = models.TextField(blank=True, null=True)
    leaf_color = models.TextField(blank=True, null=True)
    leaf_blade_texture = models.TextField(blank=True, null=True)
    presence_of_leaf_stipules = models.TextField(blank=True, null=True)
    number_of_stipules = models.IntegerField(blank=True, null=True)
    location_of_first_stipule = models.TextField(blank=True, null=True)
    leaf_attachment_to_stem = models.TextField(blank=True, null=True)
    leaf_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_width_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_length_width_ratio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    date_of_first_flowering = models.DateField(blank=True, null=True)
    flower_color = models.TextField(blank=True, null=True)
    seed_color = models.TextField(blank=True, null=True)
    pappus_color = models.TextField(blank=True, null=True)

    photo = models.ImageField(upload_to='sambong_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Sambong Characteristics {self.id}"


class SnapbeanCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='snapbean_characteristics')

    plot_no = models.TextField(blank=True, null=True)
    date_planted = models.DateField(blank=True, null=True)
    days_to_emergence = models.IntegerField(blank=True, null=True)
    emerging_cotyledon_color = models.TextField(blank=True, null=True)
    hypocotyl_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    hypocotyl_pigmentation = models.TextField(blank=True, null=True)
    leaf_shape = models.TextField(blank=True, null=True)
    growth_pattern = models.TextField(blank=True, null=True)
    leaflet_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stem_diameter = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    days_to_flowering = models.IntegerField(blank=True, null=True)
    number_of_nodes_on_main_stem_from_the_base_to_the_first = models.IntegerField(blank=True, null=True)
    flower_buds_per_inflorescence = models.IntegerField(blank=True, null=True)
    color_of_standard = models.TextField(blank=True, null=True)
    wing_opening = models.TextField(blank=True, null=True)
    colour_of_flower_wings = models.TextField(blank=True, null=True)
    duration_of_flowering = models.TextField(blank=True, null=True)
    pod_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pod_width = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pod_cross_section = models.TextField(blank=True, null=True)
    pod_suture_string = models.TextField(blank=True, null=True)
    pod_color_at_physiological_maturity = models.TextField(blank=True, null=True)
    pod_wall_fiber = models.TextField(blank=True, null=True)
    locules_per_pod = models.IntegerField(blank=True, null=True)
    pod_curvature_of_fully_expanded_immature_pod = models.TextField(blank=True, null=True)
    days_to_first_mature = models.IntegerField(blank=True, null=True)
    mature_pod_colour = models.TextField(blank=True, null=True)
    number_of_locules_per_pod = models.IntegerField(blank=True, null=True)
    pod_beak_orientation = models.TextField(blank=True, null=True)
    pod_beak_position = models.TextField(blank=True, null=True)
    pod_dehiscence = models.TextField(blank=True, null=True)
    seed_shape = models.TextField(blank=True, null=True)
    background_colour = models.TextField(blank=True, null=True)
    seed_coat_pattern = models.TextField(blank=True, null=True)
    seed_darker_color = models.TextField(blank=True, null=True)
    seed_coat_lighter_colour = models.TextField(blank=True, null=True)
    briliance_of_seed = models.TextField(blank=True, null=True)
    pattern_colour = models.TextField(blank=True, null=True)
    second_pattern_colour = models.TextField(blank=True, null=True)
    seed_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    seed_width = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    seed_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    photo = models.ImageField(upload_to='snapbean_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Snapbean Characteristics {self.id}"


class SoybeanCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='soybean_characteristics')

    plot_no = models.TextField(blank=True, null=True)
    date_planted = models.DateField(blank=True, null=True)
    days_to_emergence = models.IntegerField(blank=True, null=True)
    seedling_vigor = models.TextField(blank=True, null=True)
    hypocotyl_color = models.TextField(blank=True, null=True)
    hypocotyl_intensity_of_coloration = models.TextField(blank=True, null=True)
    leaflet_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaflet_width_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaflet_size = models.TextField(blank=True, null=True)
    number_of_leaflets = models.IntegerField(blank=True, null=True)
    plant_growth_type = models.TextField(blank=True, null=True)
    plant_growth_habit = models.TextField(blank=True, null=True)
    plant_color_of_hairs_on_the_main_stem = models.TextField(blank=True, null=True)
    petiole_presence = models.TextField(blank=True, null=True)
    leaf_blistering = models.TextField(blank=True, null=True)
    leaf_shape_of_lateral_leaflet = models.TextField(blank=True, null=True)
    leaf_intensity_of_green_color = models.TextField(blank=True, null=True)
    pubescence = models.TextField(blank=True, null=True)
    pubescence_density = models.TextField(blank=True, null=True)
    pubescence_color = models.TextField(blank=True, null=True)
    days_to_50_percent_flowering = models.IntegerField(blank=True, null=True)
    flower_keel_color = models.TextField(blank=True, null=True)
    flower_standard_color = models.TextField(blank=True, null=True)
    flower_wing_color = models.TextField(blank=True, null=True)
    days_to_first_mature_pods = models.IntegerField(blank=True, null=True)
    mature_pod_color = models.TextField(blank=True, null=True)
    pod_length_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pod_width_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    plant_height_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    seed_coat_color = models.TextField(blank=True, null=True)
    seed_coat_pattern = models.TextField(blank=True, null=True)
    hilum_color = models.TextField(blank=True, null=True)
    seed_coat_surface_luster = models.TextField(blank=True, null=True)
    strophiole_at_the_hilum = models.TextField(blank=True, null=True)
    cotyledon_color = models.TextField(blank=True, null=True)
    seed_shape = models.TextField(blank=True, null=True)
    ground_color_of_testa = models.TextField(blank=True, null=True)
    coloration_due_to_peroxidase_activity_in_seed_coat = models.TextField(blank=True, null=True)
    color_of_hilum_funicle = models.TextField(blank=True, null=True)
    number_of_pods_per_plant = models.IntegerField(blank=True, null=True)
    yield_per_plant_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ten_pod_weight_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    number_of_seeds_per_pod = models.IntegerField(blank=True, null=True)
    percentage_of_first_harvest = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    hundred_seed_weight_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    photo = models.ImageField(upload_to='soybean_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Soybean Characteristics {self.id}"


class SquashCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='squash_characteristics')

    plot_no = models.TextField(blank=True, null=True)
    date_planted = models.DateField(blank=True, null=True)
    days_to_emergence = models.IntegerField(blank=True, null=True)
    seedling_vigor = models.TextField(blank=True, null=True)
    hypocotyl_color = models.TextField(blank=True, null=True)
    hypocotyl_intensity_of_coloration = models.TextField(blank=True, null=True)
    leaflet_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaflet_width_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaflet_size = models.TextField(blank=True, null=True)
    number_of_leaflets = models.IntegerField(blank=True, null=True)
    plant_growth_type = models.TextField(blank=True, null=True)
    plant_growth_habit = models.TextField(blank=True, null=True)
    plant_color_of_hairs_on_the_main_stem = models.TextField(blank=True, null=True)
    petiole_presence = models.TextField(blank=True, null=True)
    leaf_blistering = models.TextField(blank=True, null=True)
    leaf_shape_of_lateral_leaflet = models.TextField(blank=True, null=True)
    leaf_intensity_of_green_color = models.TextField(blank=True, null=True)
    pubescence = models.TextField(blank=True, null=True)
    pubescence_density = models.TextField(blank=True, null=True)
    pubescence_color = models.TextField(blank=True, null=True)
    days_to_50_percent_flowering = models.IntegerField(blank=True, null=True)
    flower_keel_color = models.TextField(blank=True, null=True)
    flower_standard_color = models.TextField(blank=True, null=True)
    flower_wing_color = models.TextField(blank=True, null=True)
    days_to_first_mature_pods = models.IntegerField(blank=True, null=True)
    mature_pod_color = models.TextField(blank=True, null=True)
    pod_length_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pod_width_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    plant_height_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    seed_coat_color = models.TextField(blank=True, null=True)
    seed_coat_pattern = models.TextField(blank=True, null=True)
    hilum_color = models.TextField(blank=True, null=True)
    seed_coat_surface_luster = models.TextField(blank=True, null=True)
    strophiole_at_the_hilum = models.TextField(blank=True, null=True)
    cotyledon_color = models.TextField(blank=True, null=True)
    seed_shape = models.TextField(blank=True, null=True)
    ground_color_of_testa = models.TextField(blank=True, null=True)
    coloration_due_to_peroxidase_activity_in_seed_coat = models.TextField(blank=True, null=True)
    color_of_hilum_funicle = models.TextField(blank=True, null=True)
    number_of_pods_per_plant = models.IntegerField(blank=True, null=True)
    yield_per_plant_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ten_pod_weight_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    number_of_seeds_per_pod = models.IntegerField(blank=True, null=True)
    percentage_of_first_harvest = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    hundred_seed_weight_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    photo = models.ImageField(upload_to='squash_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Squash Characteristics {self.id}"


class SweetpotatoCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='sweetpotato_characteristics')

    planting_date = models.DateField(blank=True, null=True)
    sowing_date = models.DateField(blank=True, null=True)
    plot_no = models.TextField(blank=True, null=True)
    germination_rate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    twining = models.TextField(blank=True, null=True)
    length_of_main_vines = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ground_cover = models.TextField(blank=True, null=True)
    vine_internode_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    vine_internode_diameter = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    predominant_vine_color = models.TextField(blank=True, null=True)
    secondary_vine_color = models.TextField(blank=True, null=True)
    vine_tip_pubescence = models.TextField(blank=True, null=True)
    general_outline_of_the_leaf = models.TextField(blank=True, null=True)
    leaf_lobes_type = models.TextField(blank=True, null=True)
    leaf_lobe_number = models.IntegerField(blank=True, null=True)
    shape_of_central_leaf_lobes = models.TextField(blank=True, null=True)
    mature_leaf_size = models.TextField(blank=True, null=True)
    abaxial_leaf_vein_pigmentation = models.TextField(blank=True, null=True)
    mature_leaf_color = models.TextField(blank=True, null=True)
    immature_leaf_color = models.TextField(blank=True, null=True)
    petiole_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    petiole_pigmentation = models.TextField(blank=True, null=True)
    harvesting_date = models.DateField(blank=True, null=True)
    storage_root_formation = models.TextField(blank=True, null=True)
    storage_root_stalk = models.TextField(blank=True, null=True)
    number_of_storage_roots_per_plant = models.IntegerField(blank=True, null=True)
    variability_of_storage_root_size = models.TextField(blank=True, null=True)
    storage_root_shape = models.TextField(blank=True, null=True)
    variability_of_storage_root_shape = models.TextField(blank=True, null=True)
    storage_root_storage_defects = models.TextField(blank=True, null=True)
    storage_cracking = models.TextField(blank=True, null=True)
    storage_root_cortex_thickness = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    latex_production_in_storage_roots = models.TextField(blank=True, null=True)
    oxidation_in_storage_roots = models.TextField(blank=True, null=True)
    predominant_skin_color = models.TextField(blank=True, null=True)
    intensity_of_predominant_skin_color = models.TextField(blank=True, null=True)
    secondary_skin_color = models.TextField(blank=True, null=True)
    predominant_flesh_color = models.TextField(blank=True, null=True)
    secondary_flesh_color = models.TextField(blank=True, null=True)
    distribution_of_secondary_flesh_color = models.TextField(blank=True, null=True)
    flowering_habit = models.TextField(blank=True, null=True)
    flower_color = models.TextField(blank=True, null=True)
    flower_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    flower_width_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    shape_of_limb = models.TextField(blank=True, null=True)
    equality_of_sepal_length = models.TextField(blank=True, null=True)
    number_of_sepal_veins = models.IntegerField(blank=True, null=True)
    sepal_shape = models.TextField(blank=True, null=True)
    sepal_apex = models.TextField(blank=True, null=True)
    sepal_pubescence = models.TextField(blank=True, null=True)
    sepal_color = models.TextField(blank=True, null=True)
    color_of_stigma = models.TextField(blank=True, null=True)
    color_of_style = models.TextField(blank=True, null=True)
    stigma_exertion = models.TextField(blank=True, null=True)
    seed_capsule_set = models.TextField(blank=True, null=True)
    keeping_quality_of_stored_storage_roots = models.TextField(blank=True, null=True)
    sprouting_ability = models.TextField(blank=True, null=True)
    consistency_of_boiled_storage_root = models.TextField(blank=True, null=True)
    undesirable_color_of_boiled_storage_root = models.TextField(blank=True, null=True)
    texture_of_boiled_storage_root_flesh = models.TextField(blank=True, null=True)
    sweetness_of_boiled_storage_root_flesh = models.TextField(blank=True, null=True)

    photo = models.ImageField(upload_to='sweetpotato_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Sweetpotato Characteristics {self.id}"


class TaroCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='taro_characteristics')

    date_planted = models.DateField(blank=True, null=True)
    plot_number = models.TextField(blank=True, null=True)
    row_number = models.TextField(blank=True, null=True)
    characterization_date = models.DateField(blank=True, null=True)
    characterized_by = models.TextField(blank=True, null=True)
    number_of_plants = models.IntegerField(blank=True, null=True)
    number_of_stolons = models.IntegerField(blank=True, null=True)
    stolon_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    number_of_suckers = models.IntegerField(blank=True, null=True)
    plant_span = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    plant_height_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    predominant_position_shape_of_leaf_lamina_surface = models.TextField(blank=True, null=True)
    leaf_base_shape = models.TextField(blank=True, null=True)
    leaf_blade_margin = models.TextField(blank=True, null=True)
    leaf_blade_color = models.TextField(blank=True, null=True)
    leaf_blade_color_variegation = models.TextField(blank=True, null=True)
    type_of_variegation = models.TextField(blank=True, null=True)
    leaf_blade_margin_color = models.TextField(blank=True, null=True)
    leaf_lamina_appendages = models.TextField(blank=True, null=True)
    leaf_lamina_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_lamina_width = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_lamina_length_width_ratio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    petiole_junction_pattern = models.TextField(blank=True, null=True)
    petiole_junction_color = models.TextField(blank=True, null=True)
    sap_color_of_leaf_blade_tip = models.TextField(blank=True, null=True)
    leaf_main_vein_color = models.TextField(blank=True, null=True)
    leaf_main_vein_variegation = models.TextField(blank=True, null=True)
    vein_pattern = models.TextField(blank=True, null=True)
    petiole_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    petiole_length_lamina_length_ratio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    petiole_color_top_third = models.TextField(blank=True, null=True)
    petiole_color_middle_third = models.TextField(blank=True, null=True)
    petiole_color_basal_third = models.TextField(blank=True, null=True)
    petiole_stripe = models.TextField(blank=True, null=True)
    petiole_stripe_color = models.TextField(blank=True, null=True)
    petiole_basal_ring_color = models.TextField(blank=True, null=True)
    cross_section_of_lower_part_of_petiole = models.TextField(blank=True, null=True)
    sheath_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_petiole_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ratio_of_sheath_length_total_petiole_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_sheath_color = models.TextField(blank=True, null=True)
    leaf_sheath_edge_color = models.TextField(blank=True, null=True)
    leaf_waxiness = models.TextField(blank=True, null=True)
    flower_formation = models.TextField(blank=True, null=True)
    inflorescence_stalk_color = models.TextField(blank=True, null=True)
    number_of_inflorescence_leaf_axis_per_cluster = models.IntegerField(blank=True, null=True)
    number_of_floral_clusters_per_plant = models.IntegerField(blank=True, null=True)
    male_portion_of_inflorescence = models.TextField(blank=True, null=True)
    pollen_production = models.TextField(blank=True, null=True)
    pollen_color = models.TextField(blank=True, null=True)
    fertility_of_female_part_of_the_inflorescence = models.TextField(blank=True, null=True)
    sterile_appendage_male_portion_ratio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pigmentation_of_male_portion = models.TextField(blank=True, null=True)
    peduncle_length_inflorescence_length_ratio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    limb_color_upper_part_of_spathe = models.TextField(blank=True, null=True)
    tube_color = models.TextField(blank=True, null=True)
    flag_leaf_color = models.TextField(blank=True, null=True)
    spathe_shape_at_male_anthesis = models.TextField(blank=True, null=True)
    fruit_formation = models.TextField(blank=True, null=True)
    fruit_color = models.TextField(blank=True, null=True)
    number_of_berries_per_fruit_branch = models.IntegerField(blank=True, null=True)
    seed_coat_color = models.TextField(blank=True, null=True)
    seed_shape = models.TextField(blank=True, null=True)
    number_of_seeds_per_berry = models.IntegerField(blank=True, null=True)
    corm_manifestation = models.TextField(blank=True, null=True)
    corm_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    corm_branching = models.TextField(blank=True, null=True)
    corm_shape = models.TextField(blank=True, null=True)
    corm_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    corm_cortex_color = models.TextField(blank=True, null=True)
    corm_flesh_color_of_central_part = models.TextField(blank=True, null=True)
    corm_flesh_fiber_color = models.TextField(blank=True, null=True)
    corm_skin_surface = models.TextField(blank=True, null=True)
    corm_skin_thickness = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    degree_of_fibrousness_of_corm = models.TextField(blank=True, null=True)
    bud_color = models.TextField(blank=True, null=True)
    number_of_cormels = models.IntegerField(blank=True, null=True)
    weight_of_cormels = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    shape_of_cormels = models.TextField(blank=True, null=True)
    flesh_color_of_cormels = models.TextField(blank=True, null=True)
    root_color = models.TextField(blank=True, null=True)
    uniformity_in_root_color = models.TextField(blank=True, null=True)
    remar = models.TextField(blank=True, null=True)

    photo = models.ImageField(upload_to='taro_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Taro Characteristics {self.id}"


class TomatoCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='tomato_characteristics')

    sowing_date = models.DateField(blank=True, null=True)
    transplanting_date = models.DateField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    plot_no = models.TextField(blank=True, null=True)
    anthocyanin_coloration_of_hypocotyls = models.TextField(blank=True, null=True)
    stem_anthocyanin_coloration = models.TextField(blank=True, null=True)
    growth_habit = models.TextField(blank=True, null=True)
    length_of_internode = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    plant_height = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    style_pubescence = models.TextField(blank=True, null=True)
    stem_type = models.TextField(blank=True, null=True)
    stem_pubescence = models.TextField(blank=True, null=True)
    number_of_leaves_under_first_inflorescence = models.IntegerField(blank=True, null=True)
    internode_lenght_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_attitude = models.TextField(blank=True, null=True)
    leaf_type = models.TextField(blank=True, null=True)
    leaf_length_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_width_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_type_of_blade = models.TextField(blank=True, null=True)
    leaf_size_of_leaflets = models.TextField(blank=True, null=True)
    leaf_intensity_of_green_color = models.TextField(blank=True, null=True)
    leaf_size_of_leaflets_width = models.TextField(blank=True, null=True)
    leaf_glossiness = models.TextField(blank=True, null=True)
    leaf_blistering = models.TextField(blank=True, null=True)
    leaf_altitude_of_petiole_of_leaflet_in_relation_to_main_axis = models.TextField(blank=True, null=True)
    anthocyanin_coloration_of_leaf_veins = models.TextField(blank=True, null=True)
    days_to_flowering = models.IntegerField(blank=True, null=True)
    inflorescence_type = models.TextField(blank=True, null=True)
    flower_fasciation = models.TextField(blank=True, null=True)
    corolla_color = models.TextField(blank=True, null=True)
    corolla_blossom_type = models.TextField(blank=True, null=True)
    flower_sterility_type = models.TextField(blank=True, null=True)
    petal_length_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sepal_length_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    style_position = models.TextField(blank=True, null=True)
    style_shape = models.TextField(blank=True, null=True)
    style_hairiness = models.TextField(blank=True, null=True)
    stamen_length_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    exterior_color_of_immature_fruit = models.TextField(blank=True, null=True)
    presence_of_green_trips_on_the_fruit = models.TextField(blank=True, null=True)
    extent_of_green_shoulder = models.TextField(blank=True, null=True)
    intensity_of_green_color_of_shoulder = models.TextField(blank=True, null=True)
    intensity_of_green_color_excluding = models.TextField(blank=True, null=True)
    fruit_green_stripes_bfore_maturity = models.TextField(blank=True, null=True)
    number_of_days_to_commercial_maturity = models.IntegerField(blank=True, null=True)
    sensitivity_to_silvering = models.TextField(blank=True, null=True)
    ripening_uniformity = models.TextField(blank=True, null=True)
    fruit_size_at_maturity = models.TextField(blank=True, null=True)
    fruit_size_homogeneity = models.TextField(blank=True, null=True)
    fruit_shape_in_longitudinal_section = models.TextField(blank=True, null=True)
    peduncle_abscission_layer = models.TextField(blank=True, null=True)
    pedicel_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_ribbing_at_peduncle_end = models.TextField(blank=True, null=True)
    fruit_depression_at_peduncle_end = models.TextField(blank=True, null=True)
    interior_flesh_color = models.TextField(blank=True, null=True)
    interior_flesh_color_intensity = models.TextField(blank=True, null=True)
    transverse_section = models.TextField(blank=True, null=True)
    ribbing_at_calyx_end = models.TextField(blank=True, null=True)
    blossom_end_scar_size = models.TextField(blank=True, null=True)
    firmness = models.TextField(blank=True, null=True)
    shelf_life = models.TextField(blank=True, null=True)
    radial_cracking = models.TextField(blank=True, null=True)
    concentric_cracking = models.TextField(blank=True, null=True)
    fruit_fasciation = models.TextField(blank=True, null=True)
    fruit_size_variability = models.TextField(blank=True, null=True)
    exterior_color_of_mature_fruit = models.TextField(blank=True, null=True)
    intensity_of_exterior_colour = models.TextField(blank=True, null=True)
    fruit_length_in_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_width_in_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_lenght_over_width_ratio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_weight_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    color_of_flesh_at_maturity = models.TextField(blank=True, null=True)
    fruit_glossiness_of_skin = models.TextField(blank=True, null=True)
    skin_color_ripe_fruit = models.TextField(blank=True, null=True)
    number_of_locules = models.IntegerField(blank=True, null=True)
    thickness_of_pericarp = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fruit_cross_sectional_shape = models.TextField(blank=True, null=True)
    diameter_of_core_in_cross_section_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pedicel_area = models.TextField(blank=True, null=True)
    size_of_pedicel_scar = models.TextField(blank=True, null=True)
    size_of_corky_area_around_pedicel_scar = models.TextField(blank=True, null=True)
    shape_of_pistil_scar = models.TextField(blank=True, null=True)
    blossom_end_shape = models.TextField(blank=True, null=True)
    blossom_end_scar_condition = models.TextField(blank=True, null=True)
    easiness_of_peeling = models.TextField(blank=True, null=True)
    easiness_of_stem_removal = models.TextField(blank=True, null=True)
    blotchy_ripening = models.TextField(blank=True, null=True)
    soluble_solids = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    one_thousand_seed_weight_in_grams = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    photo = models.ImageField(upload_to='tomato_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Tomato Characteristics {self.id}"


class TurmericCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='turmeric_characteristics')

    days_to_emergence = models.IntegerField(blank=True, null=True)
    plant_height_at_harvest_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    basal_diameter_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pseudostem_pubescence = models.TextField(blank=True, null=True)
    leaf_pubescence = models.TextField(blank=True, null=True)
    prominence_of_leaf_venation = models.TextField(blank=True, null=True)
    spatial_arrangement_of_leaf_veins = models.TextField(blank=True, null=True)
    plicate_of_leaves = models.TextField(blank=True, null=True)
    intensity_of_green_color_in_ventral_leaf = models.TextField(blank=True, null=True)
    intensity_of_green_color_in_dorsal_leaf = models.TextField(blank=True, null=True)
    number_of_leaves_per_plant_pcs = models.IntegerField(blank=True, null=True)
    length_of_petiole_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    length_of_leaf_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    width_of_leaf_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_length_width_ratio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    days_of_first_flowering_from_planting = models.IntegerField(blank=True, null=True)
    flower_color = models.TextField(blank=True, null=True)
    length_of_peduncle_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    length_of_infloresence_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    days_to_harvest_from_planting = models.IntegerField(blank=True, null=True)
    overall_shape_of_rhizome = models.TextField(blank=True, null=True)
    density_of_adventitious_root_on_the_rhizome = models.TextField(blank=True, null=True)
    number_of_rhizomes_per_plant_pcs = models.IntegerField(blank=True, null=True)
    number_of_internodes_per_rhizome_pcs = models.IntegerField(blank=True, null=True)
    weight_of_rhizome_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    length_of_rhizome_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    diameter_of_rhizome_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    number_of_fingers_per_rhizome_pcs = models.IntegerField(blank=True, null=True)
    length_of_fingers_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    diameter_of_fingers_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fresh_color_of_rhizomes = models.TextField(blank=True, null=True)
    organoleptic_aroma_of_rhizomes = models.TextField(blank=True, null=True)

    photo = models.ImageField(upload_to='turmeric_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Turmeric Characteristics {self.id}"


class WingedbeanCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='wingedbean_characteristics')

    plot_no = models.TextField(blank=True, null=True)
    date_planted = models.DateField(blank=True, null=True)
    days_to_emergence = models.IntegerField(blank=True, null=True)
    hypocotyl_color = models.TextField(blank=True, null=True)
    hypocotyl_color_intensity = models.TextField(blank=True, null=True)
    hypocotyl_pubescence = models.TextField(blank=True, null=True)
    hypocotyl_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    plant_growth = models.TextField(blank=True, null=True)
    leaflet_size = models.TextField(blank=True, null=True)
    leaflet_shape = models.TextField(blank=True, null=True)
    stem_color = models.TextField(blank=True, null=True)
    presence_of_tuber = models.TextField(blank=True, null=True)
    tuber_size = models.TextField(blank=True, null=True)
    calyx_colour = models.TextField(blank=True, null=True)
    corolla_colour_of_wings_and_standard = models.TextField(blank=True, null=True)
    pod_colour = models.TextField(blank=True, null=True)
    presence_of_pod_specks = models.TextField(blank=True, null=True)
    pod_wing_colour = models.TextField(blank=True, null=True)
    pod_surface_texture = models.TextField(blank=True, null=True)
    pod_shape = models.TextField(blank=True, null=True)
    pod_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pod_shattering = models.TextField(blank=True, null=True)
    seed_colour = models.TextField(blank=True, null=True)
    presence_of_seed_mottling = models.TextField(blank=True, null=True)
    hilum_colour = models.TextField(blank=True, null=True)
    seed_shape = models.TextField(blank=True, null=True)
    seed_surface = models.TextField(blank=True, null=True)
    number_of_seeds_per_pod = models.IntegerField(blank=True, null=True)
    hundred_seed_weight_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    photo = models.ImageField(upload_to='wingedbean_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Wingedbean Characteristics {self.id}"


class XanthosomaCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='xanthosoma_characteristics')

    plot_no = models.TextField(blank=True, null=True)
    date_planted = models.DateField(blank=True, null=True)
    growth_habit = models.TextField(blank=True, null=True)
    length_of_above_ground_stem = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    diameter_of_above_ground_stem = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    interior_color_of_above_ground_stem = models.TextField(blank=True, null=True)
    main_axiallary_buds = models.TextField(blank=True, null=True)
    secondary_axiallary_buds = models.TextField(blank=True, null=True)
    bulbils_in_leaf_axis = models.TextField(blank=True, null=True)
    bulbis_along_stem = models.TextField(blank=True, null=True)
    petiole_attachment = models.TextField(blank=True, null=True)
    lamina_orientation = models.TextField(blank=True, null=True)
    leaf_shape = models.TextField(blank=True, null=True)
    length_of_the_breadth_of_the_lamina = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    width_of_the_breadth_of_the_lamina = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ratio_of_the_lamina = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_margin_color = models.TextField(blank=True, null=True)
    leaf_sinus_denuding = models.TextField(blank=True, null=True)
    leaf_surface_glossy = models.TextField(blank=True, null=True)
    color_of_upper_leaf_surface = models.TextField(blank=True, null=True)
    color_of_flower_leaf_surface = models.TextField(blank=True, null=True)
    leaf_variegation = models.TextField(blank=True, null=True)
    leaf_pubescence = models.TextField(blank=True, null=True)
    midrib_and_primary_lateral_veins_in_cross_section = models.TextField(blank=True, null=True)
    petiole_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    upper_petiole_color = models.TextField(blank=True, null=True)
    lower_petiole_color = models.TextField(blank=True, null=True)
    petiole_sheath_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    color_of_the_edge_of_petiole_sheath_length = models.TextField(blank=True, null=True)
    color_of_spathe_tube_on_inside = models.TextField(blank=True, null=True)
    color_of_spathe_tube_on_outside = models.TextField(blank=True, null=True)
    color_of_spathe_blade_on_inside = models.TextField(blank=True, null=True)
    color_of_spathe_constriction_on_inside = models.TextField(blank=True, null=True)
    apex_spathe = models.TextField(blank=True, null=True)
    length_of_spadix = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    color_of_sterile_flowers = models.TextField(blank=True, null=True)
    length_of_the_female_part_of_spadix = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pollen_at_anthesis = models.TextField(blank=True, null=True)
    time_to_harvest_corms = models.TextField(blank=True, null=True)
    shape_of_corm = models.TextField(blank=True, null=True)
    corm_size_at_maturity = models.TextField(blank=True, null=True)
    exterior_color_of_corms = models.TextField(blank=True, null=True)
    interior_color_of_corms = models.TextField(blank=True, null=True)
    exterior_surface_corms = models.TextField(blank=True, null=True)
    color_of_corm_apex = models.TextField(blank=True, null=True)
    position_of_corm_apex = models.TextField(blank=True, null=True)
    weight_of_corm_per_plant_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    number_of_corm_per_plant = models.IntegerField(blank=True, null=True)
    length_of_corm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    shape_of_cormels = models.TextField(blank=True, null=True)
    cormel_size_at_maturity = models.TextField(blank=True, null=True)
    exterior_color_of_cormels = models.TextField(blank=True, null=True)
    interior_color_of_cormels = models.TextField(blank=True, null=True)
    exterior_surface_cormels = models.TextField(blank=True, null=True)
    color_of_cormel_apex = models.TextField(blank=True, null=True)
    position_of_cormel_apex = models.TextField(blank=True, null=True)
    weight_of_cormels_per_plant_g = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    number_of_cormels_per_plant = models.IntegerField(blank=True, null=True)
    length_of_cormel_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    photo = models.ImageField(upload_to='xanthosoma_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Xanthosoma Characteristics {self.id}"


class YamCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='yam_characteristics')

    vigor = models.TextField(blank=True, null=True)
    stem_height_m = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stem_color = models.TextField(blank=True, null=True)
    number_of_internodes_to_first_branching = models.IntegerField(blank=True, null=True)
    internode_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    absence_or_presence_of_waxiness = models.TextField(blank=True, null=True)
    wing_size = models.TextField(blank=True, null=True)
    wing_color = models.TextField(blank=True, null=True)
    spines_on_stem_base = models.TextField(blank=True, null=True)
    position_of_leaves = models.TextField(blank=True, null=True)
    leaf_density = models.TextField(blank=True, null=True)
    leaf_color = models.TextField(blank=True, null=True)
    leaf_vein_color_upper_surface = models.TextField(blank=True, null=True)
    leaf_vein_color_lower_surface = models.TextField(blank=True, null=True)
    leaf_margin_color = models.TextField(blank=True, null=True)
    leaf_shape = models.TextField(blank=True, null=True)
    distance_between_lobes = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_width_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    position_of_the_widest_part_of_the_leaf = models.TextField(blank=True, null=True)
    tip_color = models.TextField(blank=True, null=True)
    petiole_color = models.TextField(blank=True, null=True)
    absence_or_presence_of_stipules = models.TextField(blank=True, null=True)
    absence_or_presence_of_aerial_tubers = models.TextField(blank=True, null=True)
    aerial_tuber_shape = models.TextField(blank=True, null=True)
    skin_color = models.TextField(blank=True, null=True)
    surface_texture = models.TextField(blank=True, null=True)
    flesh_color = models.TextField(blank=True, null=True)
    number_of_tubers_per_hill = models.IntegerField(blank=True, null=True)
    relationship_of_tubers = models.TextField(blank=True, null=True)
    absence_or_presence_of_corms = models.TextField(blank=True, null=True)
    corm_size = models.TextField(blank=True, null=True)
    sprouting_at_harvest = models.TextField(blank=True, null=True)
    tuber_shape = models.TextField(blank=True, null=True)
    tendency_of_tuber_to_branch = models.TextField(blank=True, null=True)
    place_where_tuber_branches = models.TextField(blank=True, null=True)
    tuber_length_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tuber_width_cm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    roots_on_the_tuber_surface = models.TextField(blank=True, null=True)
    place_of_roots_on_the_tuber = models.TextField(blank=True, null=True)
    absence_or_presence_of_cracks_on_the_tuber_surface = models.TextField(blank=True, null=True)
    tuber_skin_thickness_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tuber_skin_color_beneath_the_bark = models.TextField(blank=True, null=True)
    hardness_of_tuber = models.TextField(blank=True, null=True)
    skin_color_at_head_of_the_tuber = models.TextField(blank=True, null=True)
    flesh_color_at_central_transverse_cross_section = models.TextField(blank=True, null=True)
    flesh_color_at_lower_part_of_tuber = models.TextField(blank=True, null=True)
    uniformity_of_flesh_color_in_cross_section = models.TextField(blank=True, null=True)
    texture_of_flesh = models.TextField(blank=True, null=True)
    time_for_flesh_oxidation_after_cutting = models.TextField(blank=True, null=True)
    flesh_oxidation_color = models.TextField(blank=True, null=True)

    photo = models.ImageField(upload_to='yam_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Yam Characteristics {self.id}"


class YerbabuenaCharacteristics(models.Model):
    passportData = models.ForeignKey(PassportData, on_delete=models.SET_NULL, null=True, blank=True, related_name='yerbabuena_characteristics')

    plant_growth_habit = models.TextField(blank=True, null=True)
    branching_density = models.TextField(blank=True, null=True)
    stem_color = models.TextField(blank=True, null=True)
    stem_hairiness = models.TextField(blank=True, null=True)
    stem_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_shape = models.TextField(blank=True, null=True)
    leaf_apex_shape = models.TextField(blank=True, null=True)
    leaf_base_shape = models.TextField(blank=True, null=True)
    leaf_blade_color = models.TextField(blank=True, null=True)
    pubescence_density_of_upper_adaxial_leaf_surface = models.TextField(blank=True, null=True)
    leaf_length_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    leaf_width_mm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    date_of_first_flowering_from_planting = models.DateField(blank=True, null=True)
    corolla_color = models.TextField(blank=True, null=True)
    shape_of_calyx = models.TextField(blank=True, null=True)
    pubescence_density_of_corolla = models.TextField(blank=True, null=True)
    seed_color = models.TextField(blank=True, null=True)

    photo = models.ImageField(upload_to='yerbabuena_characteristics/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.passportData and self.passportData.accession_number:
            return self.passportData.accession_number
        if self.passportData and self.passportData.gb_number:
            return self.passportData.gb_number
        if self.passportData and self.passportData.old_accession_number:
            return self.passportData.old_accession_number
        return f"Yerbabuena Characteristics {self.id}"



