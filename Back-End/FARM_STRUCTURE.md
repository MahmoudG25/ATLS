# FARM STRUCTURE

## Models

### Farm

* name

### CropType

* name (Palm / Olive)

### Sector

* name
* farm (FK)
* crop_type (FK)

### Plot (Hosh)

* name
* sector (FK)
* is_general (bool)  # لو القطاع بدون حوش

## Rules

* Sector لازم يكون مرتبط بنوع محصول
* Plot ممكن يكون:

  * موجود (حوش)
  * أو القطاع كله بدون حوش

## Notes

* كل العمليات هترتبط بـ Sector أو Plot
