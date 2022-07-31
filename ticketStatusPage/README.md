# Custom Ticket Status List

Currently only integrated with Jira, creates a custom markdown file with ticket statuses in defined order. Also get extra tickets in specific Epics incase any are missed.

## Usage

1. Install requirements with `make install`

2. Update config files with your values

   - `authSecret.py`
   - `configSecret.py`

3. Run the script with `make run`

## Testing

There are tests for the script, you can run them with `make test`
