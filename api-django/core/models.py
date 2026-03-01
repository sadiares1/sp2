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


