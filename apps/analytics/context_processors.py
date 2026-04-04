"""Context processors for analytics app."""

import os


def analytics_context(request):
    """
    Add analytics configuration to template context.
    
    Makes GA_MEASUREMENT_ID available in all templates.
    """
    ga_measurement_id = os.getenv('GA_MEASUREMENT_ID', '')
    
    return {
        'GA_MEASUREMENT_ID': ga_measurement_id,
    }
