# WAREHOUSE

## Categories

* tools
* pesticides
* fertilizers

## Models

### Item

* name
* category
* quantity

### Movement

* item (FK)
* type (IN / OUT)
* quantity
* date

## Notes

* track changes via movements
* do NOT update quantity manually
