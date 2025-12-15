#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    """Run administrative tasks."""
    # ✅ الإصلاح: تحديد المسار الصحيح لإعدادات Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogicum.settings')
    
    # ✅ الإصلاح: إضافة المسار الصحيح لـ Python
    current_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_path)  # أضف المجلد الحالي
    sys.path.insert(0, os.path.join(current_path, 'blogicum'))  # أضف blogicum
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
