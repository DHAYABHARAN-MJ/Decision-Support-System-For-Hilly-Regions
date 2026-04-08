#!/usr/bin/env python
import os, sys
def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hill_dss.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Install Django: pip install django djangorestframework") from exc
    execute_from_command_line(sys.argv)
if __name__ == '__main__':
    main()
