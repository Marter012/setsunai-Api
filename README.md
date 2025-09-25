# Setsunai API Documentation

## Índice

1. [Introducción](#introducción)  
2. [Endpoints de Pieces](#endpoints-de-pieces)  
   - [GET /pieces](#get-pieces)  
   - [POST /addPiece](#post-addpiece)  
   - [PUT /pieces/{code}](#put-piecescode)  
3. [Endpoints de CombinedPieces](#endpoints-de-combinedpieces)  
   - [GET /combinedPieces](#get-combinedpieces)  
   - [POST /addCombinedPiece](#post-addcombinedpiece)  
   - [PUT /combinedPieces/{code}](#put-combinedpiecescode)  

---

## Introducción

La API de **Setsunai** permite gestionar **piezas individuales** y **combinados de piezas**.  
Está desarrollada con **FastAPI** y utiliza **MongoDB** como base de datos principal.

---

## Endpoints de Pieces

### GET `/pieces`

Obtiene la lista de todas las piezas registradas.

**Respuesta:**

```json
[
  {
    "_id": "64abc123...",
    "code": "PC001",
    "name": "Puchero chico",
    "description": "Descripción de la pieza",
    "img": "url_de_imagen",
    "state": true
  }
]
```
POST /addPiece
Agrega una nueva pieza.

Cuerpo de la solicitud:

{
  "name": "Nombre de la pieza",
  "description": "Descripción",
  "img": "URL de la imagen"
}
Respuestas:

200 OK

{
  "message": "Pieza agregada correctamente",
  "piece": { ... }
}
400 Bad Request → El nombre ya existe.

PUT /pieces/{code}
Actualiza una pieza existente mediante su código.

Cuerpo de la solicitud:

{
  "name": "Nuevo nombre opcional",
  "description": "Nueva descripción opcional",
  "img": "Nueva URL opcional",
  "state": true
}
Respuestas:

200 OK

{
  "message": "Pieza actualizada con éxito",
  "piece": { ... }
}
400 Bad Request → El nombre ya existe.

404 Not Found → Código no encontrado.

Endpoints de CombinedPieces
GET /combinedPieces
Obtiene todos los combinados de piezas.

Respuesta:

[
  {
    "_id": "64def456...",
    "code": "CP001",
    "name": "Combinado especial",
    "img": "url_de_imagen",
    "typePieces": "PC001,PC002",
    "state": true
  }
]
POST /addCombinedPiece
Agrega un nuevo combinado de piezas.

Cuerpo de la solicitud:

{
  "name": "Nombre del combinado",
  "img": "URL de la imagen",
  "typePieces": "PC001,PC002"
}
Respuestas:

200 OK

{
  "message": "Combinado agregado correctamente",
  "combinedPiece": { ... }
}
400 Bad Request → El nombre ya existe.

PUT /combinedPieces/{code}
Actualiza un combinado existente mediante su código.

Cuerpo de la solicitud:

{
  "name": "Nuevo nombre opcional",
  "img": "Nueva URL opcional",
  "typePieces": "PC001,PC002",
  "state": true
}
Respuestas:

200 OK

{
  "message": "Combinado actualizado correctamente",
  "combinedPiece": { ... }
}
400 Bad Request → El nombre ya existe.

404 Not Found → Código no encontrado.

