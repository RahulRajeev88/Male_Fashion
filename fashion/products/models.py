import os


from django.db import models
from django.utils.text import slugify
from django.core.files.uploadedfile import SimpleUploadedFile


from PIL import Image
from io import BytesIO




class Category(models.Model):
    name = models.CharField(max_length=200)
    is_blocked = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'categories'


class ProductSize(models.Model):
    name = models.CharField(max_length=50)
    stock_unit = models.IntegerField()

    def __str__(self):
        return self.name






class Product(models.Model):

    LIVE = 1
    DELETE = 0
    DELETE_CHOICES = ((LIVE,'Live'),(DELETE,'Delete'))



    title = models.CharField(max_length=200)
    price = models.FloatField()
    image = models.ImageField(upload_to='media/')
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    short_description = models.CharField(max_length=200)
    size = models.ForeignKey(ProductSize, on_delete=models.CASCADE) 
    is_show = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)
    delete_status = models.IntegerField(choices=DELETE_CHOICES,default=LIVE)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return self.title
    
    def save(self,*args, **kwargs):
        slug = slugify(self.title)

        unique_id = str(uuid.uuid4().hex[:6])
        slug = f"{slug}-{unique_id}"

        self.slug = slug
        super().save(*args, **kwargs)

        with open(self.image.path, 'rb') as img_file:
            img = Image.open(img_file)
            img = img.resize((262, 260),Image.Resampling.LANCZOS)
            img.save(self.featured_image.path, img.format)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_image')
    image = models.ImageField(upload_to='media',blank=True,null=True)
    thumbnail = models.ImageField(upload_to='thumbnails',blank=True,null=True)
    is_show = models.BooleanField(default=True)


    def save(self,*args, **kwargs):
        super().save(*args, **kwargs)

        if not self.thumbnail:
            if self.image:
                with open(self.image.path, 'rb') as img_file:
                    img = Image.open(img_file)
                    img = img.resize((300,533), Image.LANCZOS)

                    thumbnail_img = img.copy()
                    thumbnail_img.thumbnail((100,120), Image.LANCZOS)


                    thumb_filename = os.path.basename(self.image.path)
                    thumb_io = BytesIO()
                    thumbnail_img.save(thumb_io, format='JPEG' ,quality=90)
                    thumb_file = SimpleUploadedFile(thumb_filename,thumb_io.getvalue(), content_type='image/jpeg')
                    self.thumbnail.save(thumb_filename,thumb_file, save=False)
                    self.image.save(thumb_filename,thumb_file, save=False)

                


    