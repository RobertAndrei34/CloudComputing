# Development Process

## Problems Encountered

- Keeping the system simple enough for an academic MVP while still demonstrating distributed cloud concepts.
- Avoiding external paid services for SMS/email.
- Designing asynchronous event processing without overcomplicating the user interface.

## Solutions Adopted

- Redis was added for queue snapshot caching.
- RabbitMQ was added for event-driven communication.
- A separate worker container was added to process notification events.
- Notifications are simulated in the database instead of being sent through paid SMS/email providers.

## Limitations

- Notification delivery is simulated.
- Deployment must still be configured manually in a public cloud platform.
- Redis is used for cache, not as the primary data source.
- RabbitMQ is used for notification events only in this MVP.

## AI Tools Usage

AI tools were used for documentation drafting, architecture planning, code generation and implementation guidance. The final project must be reviewed, understood and explained by the team.
