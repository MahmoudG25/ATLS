# PALM MODULE

## Level

Data stored per Plot

## Fields

* plot (FK)
* trees_count
* palm_type
* trees_age
* last_year_production
* expected_production
* offshoots_count
* sold_offshoots

## Logic

* expected_production optional (manual or calculated)
* validate trees_count > 0

## Notes

* One record per plot per year (optional later)
