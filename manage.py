#!/usr/bin/env python
import os
import sys

# أضف هذا السطر
sys.path.append(os.path.join(os.path.dirname(__file__), 'blogicum'))

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogicum.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
