# Create your models here.
from django.db import models
from django.contrib.gis.db import models as gis_models
from usuarios.models import Usuario

class Geocerca (models.Model):

  """Define el primetro virtual del Centro Minero"""

nombre = models.CharField(max_length=100, default="Centro Minero SENA")
descripcion = models.TextField(blank=True)

# coordenadas de periemtro (poligono)
poligono = gis_models.PolygonFiel()

# radio de tolerancia en  metros 
radio_tolerancia = models.IntegerField(default=50)

activa = models.BooleanField(default=True)
fecha_creacion = models.DateTimeField(auto_now_add=True)

class Meta:
    verbose_name = 'Georcerca'
    verbose_name_prural = 'Geocercas'

def __str__(self):
    return self.nombre

def punto_esta_dentro(self, latitud, longitud):
    """Verifica si un punto esta dentro geocecar"""
    from django.contrib.gis.geos import point
    punto = point(longitud, latitud)
    return self.poligono.contains(punto)

class RegistroAcceso(models.Model):
    """Registra cada ingreso y egreso del centro"""

    TIPO_ACCESO = [
        ('INGRESO', 'Ingreso'),
        ('EGRESO', 'Egreso'),
    ]

    METODO_DETECCION = [
        ('AUTOMATICO', 'Deteccion Automatica'),
        ('MANUAL', 'Registro Manual'),
        ('QR', 'codigo QR'),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='accesos')
    tipo = models.CharField(max_length=10, choices=TIPO_ACCESO)
    
    # Datos del ingreso
    fecha_hora_ingreso = models.DateTimeField(auto_now_add=True)
    ubicacion_ingreso = gis_models.PointField(null=True, blank=True)
    metodo_ingreso = models.CharField(max_length=15, choices=METODO_DETECCION, default='AUTOMATICO')
    
    # Datos del egreso
    fecha_hora_egreso = models.DateTimeField(null=True, blank=True)
    ubicacion_egreso = gis_models.PointField(null=True, blank=True)
    metodo_egreso = models.CharField(max_length=15, choices=METODO_DETECCION, null=True, blank=True)
    
    # Información adicional
    dispositivo_id = models.CharField(max_length=100, blank=True)
    notas = models.TextField(blank=True)

class Meta:
    verbose_name = 'Registro de Acceso'
    verbose_name_plural = 'Registros de Acceso'
    vordering = ['-fecha_hora_ingreso']
    indexes = [
        models.Index(fields=['usuario', '-fecha_hora_ingreso']),
        models.Index(fields=['fecha_hora_ingreso']),
    ]
    
def __str__(self):
    return f"{self.usuario} - {self.tipo} - {self.fecha_hora_ingreso}"
    
@property
def duracion_permanencia(self):
    """Calcula el tiempo de permanencia en el centro"""
    if self.fecha_hora_egreso:
        return self.fecha_hora_egreso - self.fecha_hora_ingreso
    return None

class ConfiguracionAforo (models.Model):
    """Configuración de aforo máximo del centro"""
    
    aforo_maximo = models.IntegerField(default=2000)
    aforo_alerta = models.IntegerField(default=1800)  # 90% del máximo
    mensaje_alerta = models.TextField(
        default="Se está alcanzando el aforo máximo del centro"
    )
    activo = models.BooleanField(default=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
class Meta:
    verbose_name = 'Configuración de Aforo'
    verbose_name_plural = 'Configuraciones de Aforo'
    
def __str__(self):
        return f"Aforo Máximo: {self.aforo_maximo}"
    
@classmethod
def get_aforo_actual(cls):
    """Obtiene el número de personas actualmente en el centro"""
    from django.db.models import Q
    return RegistroAcceso.objects.filter(
        Q(fecha_hora_egreso__isnull=True) | 
        Q(fecha_hora_egreso__gt=models.F('fecha_hora_ingreso'))
).count()