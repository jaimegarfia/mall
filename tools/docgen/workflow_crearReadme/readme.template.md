# MS <NOMBRE_MICRO>

## Descripción del proyecto  

  <DESC_MICRO>

## Instalación  

Antes de comenzar, asegúrate de contar con los siguientes requisitos:

1.  **Entorno local**:

    -   **Java 17** instalado.
    -   **Gradle 7.3** o superior.

2.  **Infraestructura**:

    -   **Kubernetes** configurado y accesible.
    -   **ArgoCD** instalado en el clúster para la gestión de despliegues.
    -   **Jenkins** configurado con los pipelines requeridos.
3.  **Credenciales y accesos**:

    -   Acceso a los repositorios de código y a los entornos configurados (como el repositorio Git para ArgoCD).
    -   Variables de entorno o secretos requeridos (p. ej., credenciales de Docker Registry, acceso a bases de datos, etc.).
    - 
### Instalación en el Entorno Local

#### 1. Clonar el repositorio

Clona el repositorio del proyecto:

## Ejemplo de bloque de código  
Para consultar los tickets facturados, puedes usar el siguiente código Java:  

      git clone <URL_DEL_REPOSITORIO> 
      cd <NOMBRE_MICRO>

 
### 2. Configurar el entorno

Coger el archivo `application.yml` desde la carpeta live-infra y copiarlo en `src/main/resources/application.yml` según sea necesario para tu entorno local.

### 3. Compilar el proyecto

Ejecuta el siguiente comando para compilar el proyecto:

    ./gradlew clean build

### 4. Ejecutar el microservicio

Inicia la aplicación:

    java -jar build/libs/<NOMBRE_DEL_JAR>.jar

   
### Propiedades básicas Spring  

## Descripción General

Este README proporciona información esencial sobre la configuración y el despliegue de la aplicación `<NOMBRE_MICRO>`. La aplicación está construida utilizando Spring Boot y está diseñada para interactuar con los servicios asociados.

## Configuración

### Perfiles de Spring
Esta sección define el perfil activo de Spring, permitiendo configuraciones específicas para cada entorno. La sintaxis `${ENVIRONMENT:local}` significa que si la variable `ENVIRONMENT` no está establecida, se utilizará `local` como valor por defecto. Esto es crucial para gestionar diferentes configuraciones para desarrollo, pruebas y producción.

    spring:
      profiles:
        active: ${ENVIRONMENT:local}

### Metadatos de la Aplicación

 Especifica el nombre de la aplicación y el ID del módulo para su identificación dentro de una arquitectura de microservicios.
 
    application:
      name: <APP_NAME>
      moduleid: <APP_MODULEID>

### Tareas Programadas
Configura tareas programadas para ejecutarse a una tasa fija de 60 segundos.

    scheduled:
      tokenscope:
        fixedRate: 60000

### Configuración de Endpoints

Configura el endpoint de salud para que no sea sensible, permitiendo el acceso público al estado de salud.

    endpoints:
      health:
        sensitive: false

### Configuración del Servidor
Define la ruta de contexto para la aplicación, que es útil para el enrutamiento de solicitudes.

    server:
      context-path: /<NOMBRE_MICRO>

### Configuración del Cliente Eureka

 Desactiva el cliente Eureka, indicando que esta aplicación no se registrará en un servidor Eureka para el descubrimiento de servicios.
 
    eureka:
      client:
        enabled: false


### Seguridad de la Arquitectura Carrefour
Habilita las características de seguridad y especifica la URL para los scopes de cliente en la arquitectura Carrefour.

    carrefour:
      arch:
        security:
          enabled: true
          client-scopes-url: https://security-dev.npapps.ocp.es.wcorp.carrefour.com/service-auth-server-v1/scopesApps?scopeApp={scopeApp}


### Configuración de Seguridad

 Configura los ajustes de seguridad, particularmente para el acceso a recursos OAuth2. El `keyUri` proporciona la ubicación de la clave pública para la validación de JWT.

    security:
      strategy: MODE_INHERITABLETHREADLOCAL
      oauth2:
        resource:
          c4:
            jwt:
              keyUri: https://security-dev.npapps.ocp.es.wcorp.carrefour.com/service-auth-server-v1/keystore/public
    
## Dependencias  

<TEMPLATE_KUDU>

<TEMPLATE_SOLR>

#### Configuración de Kerberos
```yaml
kerberos:
  filePath:
    krb5:
      file: /etc/kerberos/conf/krb5.conf
      debug: false
    jaas:
      file: /etc/kerberos/jaas/kerberos.jaas
      useSubjectCredsOnly: true
<TEMPLATE_KERBEROS_KUDU>
```
Esta sección proporciona la configuración para la autenticación Kerberos. Incluye la ruta al archivo de configuración de Kerberos, la ruta al archivo de configuración JAAS, el reino de Kerberos, el nombre de usuario para la autenticación y la ruta a los ficheros necesarios para la autenticación.


## Modelo de Datos  

A continuación se presenta el modelo de datos basado en las clases Java proporcionadas, estructurado de acuerdo con la colección de documentos de referencia.

<MODELO_DATOS>
    
## Api  

El api se encuentra documentada con swagger OpenAPI 3.0.1. La url será 

XXX/<NOMBRE_MICRO>/swagger-ui/index.html

donde XXX es el valor de

     externalHostName: <EXTERNAL_HOSTNAME>

que dependerá de cada entorno
 
## Recursos estimados  

A continuación se detallan los requisitos mínimos de recursos para el contenedor, basados en la configuración proporcionada:

-   CPU:
    
    -   Límite máximo: `<MAX_CPU>` núcleo de CPU.
    -   Mínimo solicitado: `<MIN_CPU>m` (<MIN_CPU> milicores de CPU).
        -   Interpretación: Esto significa que el contenedor solicitará un mínimo de <MIN_CPU> milicores (m) de CPU, garantizando así que tenga acceso a recursos de CPU suficientes para funcionar adecuadamente.
-   Memoria:
    
    -   Límite máximo: `<MAX_MEM>Mi`.
    -   Mínimo solicitado: `<MIN_MEM>Mi`.
        -   Interpretación: El contenedor solicitará un mínimo de <MIN_MEM> Mebibytes (Mi) de memoria, asegurando que tenga los recursos necesarios para operar sin problemas. Esta información se deriva de la configuración inicial proporcionada.
