# Rating system implementation notes

## Policy
- A rating is tied to a completed PurchaseOrder.
- Buyer and seller can rate one another.
- Only the requester of a completed logistics/inspection service can rate its assigned provider.
- Logistics must be `delivered`; inspection must be `completed`.
- One reviewer can rate a given participant once per purchase order.
- Overall and dimension scores are 1–5. Dimension names are validated server-side by the reviewed user's role.
- Financier, insurer, product-level, and other ratings are not implemented in this MVP.

## API
The endpoint is registered under `/api/v1/ratings` (slash-less, matching this project's API convention).

Create a rating with an authenticated POST request:
```json
{
  "purchase_order": 12,
  "reviewed": 34,
  "overall_score": 5,
  "dimensions": {
    "product_quality": 5,
    "quantity_accuracy": 4,
    "delivery": 5,
    "communication": 4
  },
  "comment": "Goods matched the agreed specification."
}
```
The `reviewer` is always taken from the authenticated user; clients cannot submit it. `requested_by` on service requests is also assigned by the backend and is read-only to clients.

## Migration and historical records
Run `python manage.py migrate` in the backend environment. The new `requested_by` fields are nullable to allow existing rows to migrate without inventing historical requester identities. Existing service requests with no known requester will not qualify for service-provider ratings; newly created requests are assigned a requester automatically.

## Validation note
```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py test
```
