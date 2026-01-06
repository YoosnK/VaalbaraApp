from django.db import models

class Partner(models.Model):
    #partner_id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=200, blank=True)
    tax_code = models.CharField(max_length=200)

    def __str__(self):
        return self.name