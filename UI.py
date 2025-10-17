import streamlit as st
import pandas as pd
import os
import sys
import subprocess
import tempfile
from datetime import datetime, date, time, timedelta
import importlib.util
import traceback
import itertools
import json
import os
from typing import Dict, List, Optional, Any, Tuple, Union

# =============================================================================
# PAGE CONFIGURATION - MUST BE FIRST STREAMLIT COMMAND
# =============================================================================

st.set_page_config(
    page_title="Hospital Scheduling System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CUSTOMIZABLE STYLING SECTION
# You can easily modify colors here or delete this entire section
# =============================================================================

def apply_custom_styling():
    """
    Apply custom CSS styling to the Streamlit interface.
    
    This function contains all the custom styling code in one place,
    making it easy to modify colors or completely remove styling
    without affecting the rest of the application.
    
    To change the button hover color, modify the --hover-color variable below.
    To remove all custom styling, simply delete this entire function
    and remove the apply_custom_styling() call from main().
    """
    st.markdown("""
    <style>
    :root {
        --hover-color: #6000FF;  /* Change this to your preferred hover color */
        --primary-color: #6000FF;
    }
    
    /* Custom button hover effects */
    .stButton > button:hover {
        background-color: var(--hover-color) !important;
        border-color: var(--hover-color) !important;
        color: white !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 16px;
        font-weight: 500;
    }
    
    /* Make important buttons more prominent */
    .stButton > button[kind="primary"] {
        background-color: var(--primary-color);
        border-color: var(--primary-color);
    }
    
    /* Success/error message styling */
    .stSuccess, .stError, .stWarning, .stInfo {
        font-size: 14px;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# =============================================================================
# TRANSLATION SYSTEM
# =============================================================================

TRANSLATIONS = {
    'da': {  # Danish (default language)
        # Main interface
        'app_title': 'Vagtplanlægningssystem',
        'app_subtitle': 'Administrer personale, vagter og begrænsninger',
        
        # Language selection
        'language': 'Sprog',
        'english': 'English',
        'danish': 'Dansk',
        
        # Tabs
        'employees_tab': 'Medarbejdere',
        'shifts_tab': 'Vagter', 
        'constraints_tab': 'Begrænsninger',
        'run_model_tab': 'Kør Model',
        
        # Common buttons
        'add': 'Tilføj',
        'remove': 'Fjern',
        'save': 'Gem',
        'cancel': 'Annuller',
        'edit': 'Rediger',
        'delete': 'Slet',
        'refresh': 'Opdater',
        'run': 'Kør',
        
        # Employee fields
        'employee_id': 'Medarbejder-ID',
        'employee_id_required': 'Medarbejder-ID (påkrævet)',
        'nickname': 'Kaldenavn',
        'title': 'Titel',
        'weekly_hours': 'Ugentlige timer',
        'shift_types': 'Vagttyper',
        'hourly_wage': 'Timeløn',
        'norm_period_start': 'Normperiodestart',
        'norm_period_end': 'Normperiodeslutning',
        'hour_deficit': 'Timeunderskud',
        'current_night_shifts': 'Nuværende nattevagter',
        'current_evening_night_shifts': 'Nuværende aften/nattevagter',
        
        # Shift fields
        'shift_id': 'Vagtnavn',
        'shift_id_required': 'Vagtnavn (påkrævet)',
        'start_time': 'Starttid',
        'end_time': 'Sluttid',
        'shift_category': 'Vagtkategori',
        
        # Constraint management
        'constraint_type': 'Begrænsningstype',
        'hard_constraints': 'Hårde begrænsninger',
        'soft_constraints': 'Bløde begrænsninger',
        'employee_specific': 'Medarbejderspecifik',
        'general_constraints': 'Generelle begrænsninger',
        'select_employee': 'Vælg medarbejder',
        'select_employees': 'Vælg medarbejdere',
        'select_constraint': 'Vælg begrænsning',
        'constraint_parameters': 'Begrænsningsparametre',
        'weight': 'Vægt',
        'multiple_values_help': 'Hold Ctrl/Cmd for at vælge flere',
        'combinations_will_be_created': 'Der vil blive oprettet begrænsninger for alle kombinationer',
        
        # Model running - ENHANCED DATE TRANSLATIONS
        'model_settings': 'Modelindstillinger',
        'scheduling_period': 'Vagtplanperiode',
        'start_date': 'Startdato',
        'end_date': 'Slutdato',
        'date_range_preset': 'Hurtigt valg',
        'custom_range': 'Brugerdefineret periode',
        'current_month': 'Denne måned',
        'next_month': 'Næste måned',
        'current_week': 'Denne uge',
        'next_week': 'Næste uge',
        'max_time_seconds': 'Maksimal tid (sekunder)',
        'run_model': 'Kør model',
        'model_running': 'Model kører...',
        'model_success': 'Model kørt!',
        'model_error': 'Fejl ved kørsel af model',
        'invalid_date_range': 'Ugyldigt datointerval',
        'end_before_start': 'Slutdato skal være efter startdato',
        'scheduling_for': 'Planlægger for',
        'days_total': 'dage i alt',
        
        # NEW: Date-specific translations
        'date_input_method': 'Datoinputmetode',
        'select_individual_dates': 'Vælg enkelte datoer',
        'specify_date_range': 'Angiv dato interval',
        'individual_dates': 'Individuelle datoer',
        'date_range': 'Datointerval',
        'from_date': 'Fra dato',
        'to_date': 'Til dato',
        'selected_dates': 'Valgte datoer',
        
        # Messages
        'no_data': 'Ingen data tilgængelig',
        'data_saved': 'Data gemt',
        'data_loaded': 'Data indlæst',
        'invalid_data': 'Ugyldige data',
        'required_field': 'Dette felt er påkrævet',
        'constraint_added': 'Begrænsning tilføjet',
        'constraints_added': 'begrænsninger tilføjet',
        'constraint_removed': 'Begrænsning fjernet',
        
        # File paths
        'data_files': 'Datafiler',
        'employees_file': 'Medarbejderfil',
        'shifts_file': 'Vagtfil',
        'hard_constraints_file': 'Hårde begrænsninger-fil',
        'soft_constraints_file': 'Bløde begrænsninger-fil',
        
        # Help text
        'employee_id_help': 'Unikt ID for medarbejderen',
        'shift_id_help': 'Unikt navn for vagten',
        'constraint_help': 'Hårde begrænsninger bliver altid overholdt. Bløde begrænsninger bliver overholdt hvis muligt.',
        'date_range_help': 'Vælg start- og slutdato for vagtplanlægningsperioden',
        'date_input_help': 'Vælg specifikke datoer eller angiv et dato interval',
        
        # New flexible parameter translations
        'targeting_method': 'Vælg targeting metode:',
        'specific_shift': 'Specifik vagt',
        'shift_category': 'Vagt kategori',
        'multiple_categories': 'Flere kategorier',
        'column_name': 'Kolonne navn',
        'column_value': 'Kolonne værdi',
        'column_values': 'Kolonne værdier',
        'column_name_help': 'Vælg hvilken kolonne der skal matches',
        'column_value_help': 'Værdien der skal matches i den valgte kolonne',
        'column_values_help': 'Komma-separeret liste af værdier',

        # Historical schedule translations
        'historical_schedule': 'Tidligere vagtplan',
        'use_historical_data': 'Brug tidligere vagtplansdata',
        'load_historical_schedule': 'Indlæs tidligere vagtplan',
        'upload_method': 'Vælg indlæsningsmetode',
        'upload_file': 'Upload fil',
        'specify_path': 'Angiv sti',
        'choose_excel_file': 'Vælg Excel fil med tidligere vagtplan',
        'file_format_help': 'Filen skal indeholde medarbejder-ID\'er som rækker og datoer som kolonner',
        'file_uploaded_successfully': 'Fil uploadet',
        'file_preview': 'Forhåndsvisning af fil',
        'historical_data_info': 'Tidligere data',
        'could_not_parse_dates': 'Kunne ikke indlæse datokolonner',
        'error_reading_file': 'Fejl ved læsning af fil',
        'path_to_historical_file': 'Sti til fil med tidligere vagtplan',
        'specify_full_path': 'Angiv den fulde sti til Excel-filen',
        'file_found': 'Fil fundet',
        'file_not_found': 'Fil ikke fundet',
        'show_preview': 'Vis forhåndsvisning',
        'format_help': 'Formathjælp',
        'expected_file_format': 'Forventet filformat',
        'format_rules': 'Regler',
        'first_column_employee_ids': 'Første kolonne: Medarbejder ID\'er',
        'other_columns_dates': 'Øvrige kolonner: Datoer i YYYY-MM-DD format',
        'cells_shift_ids': 'Celler: Vagt ID\'er (f.eks. \'DAG\', \'NAT\') eller tomme for fridage',
        'extended_calendar_info': 'Med tidligere vagtplansdata vil kalenderen blive udvidet til at inkludere både tidligere og fremtidige datoer',
        'extended_calendar': 'Udvidet kalender',
        'historical_days': 'Tidligere dage',
        'new_days': 'Nye dage',
        'total_days': 'Total',
        'historical_integration_success': 'Tidligere vagtplan integreret',

        'file_input_method': 'Filinputmetode',
        'browse_for_file': 'Gennemse for fil',
        'specify_file_path': 'Angiv fil sti',
        'choose_file': 'Vælg fil',
        'file_selected': 'Fil valgt',
        'upload_or_specify': 'Upload eller angiv',

        'app_title': 'Vagtplansystem',
        'app_subtitle': 'Administrer personale, vagter og begrænsninger',
        'language': 'Sprog',
        'english': 'English',
        'danish': 'Dansk',
        'employees_tab': 'Medarbejdere',
        'shifts_tab': 'Vagter', 
        'constraints_tab': 'Begrænsninger',
        'run_model_tab': 'Kør Model',

        'add_date': 'Tilføj dato',
        'add_column': 'Tilføj kolonne',

        'delete_column': 'Slet Kolonne',
        'show_all_columns': 'Vis alle kolonner', 
        'select_column_to_delete': 'Vælg kolonne til sletning',
        'delete_column_help': 'Vælg hvilken kolonne der skal slettes permanent',
        'delete_warning': '⚠️ **Advarsel:** Denne handling kan ikke fortrydes! Kolonnen og alle dens data vil blive permanent slettet.',
        'confirm_delete': '🗑️ Bekræft Sletning',
        'column_deleted_successfully': 'Kolonne \'{}\' slettet succesfuldt!',
        'no_columns_for_deletion': 'Ingen kolonner tilgængelige til sletning',
        'close': 'Luk',

        'tools_tab': 'Værktøjer',
        'rest_hours': 'Minimum timers hvil',

        "add_shift_button": "Tilføj vagter",

        "save_shifts_button": "Gem vagter",

        "save_changes": "Gem ændringer",
        "column_type": "Kolonnetype",

        "text": "Tekst",
        "number": "Tal",
        "date": "Dato",
        "time": "Klokkeslet"
    },
    
    'en': {  # English
        # Main interface
        'app_title': 'Hospital Scheduling System',
        'app_subtitle': 'Manage staff, shifts, and constraints',
        
        # Language selection
        'language': 'Language',
        'english': 'English',
        'danish': 'Dansk',
        
        # Tabs
        'employees_tab': 'Employees',
        'shifts_tab': 'Shifts',
        'constraints_tab': 'Constraints',
        'run_model_tab': 'Run Model',
        
        # Common buttons
        'add': 'Add',
        'remove': 'Remove',
        'save': 'Save',
        'cancel': 'Cancel',
        'edit': 'Edit',
        'delete': 'Delete',
        'refresh': 'Refresh',
        'run': 'Run',
        
        # Employee fields
        'employee_id': 'Employee ID',
        'employee_id_required': 'Employee ID (required)',
        'nickname': 'Nickname',
        'title': 'Title',
        'weekly_hours': 'Weekly hours',
        'shift_types': 'Shift types',
        'hourly_wage': 'Hourly wage',
        'norm_period_start': 'Norm period start',
        'norm_period_end': 'Norm period end',
        'hour_deficit': 'Hour deficit',
        'current_night_shifts': 'Current night shifts',
        'current_evening_night_shifts': 'Current evening/night shifts',
        
        # Shift fields
        'shift_id': 'Shift ID',
        'shift_id_required': 'Shift ID (required)',
        'start_time': 'Start time',
        'end_time': 'End time',
        'shift_category': 'Shift category',
        
        # Constraint management
        'constraint_type': 'Constraint type',
        'hard_constraints': 'Hard constraints',
        'soft_constraints': 'Soft constraints',
        'employee_specific': 'Employee-specific',
        'general_constraints': 'General constraints',
        'select_employee': 'Select employee',
        'select_employees': 'Select employees',
        'select_constraint': 'Select constraint',
        'constraint_parameters': 'Constraint parameters',
        'weight': 'Weight',
        'multiple_values_help': 'Hold Ctrl/Cmd to select multiple',
        'combinations_will_be_created': 'Constraints will be created for all combinations',
        
        # Model running - ENHANCED DATE TRANSLATIONS
        'model_settings': 'Model settings',
        'scheduling_period': 'Scheduling period',
        'start_date': 'Start date',
        'end_date': 'End date',
        'date_range_preset': 'Quick selection',
        'custom_range': 'Custom range',
        'current_month': 'Current month',
        'next_month': 'Next month',
        'current_week': 'Current week',
        'next_week': 'Next week',
        'max_time_seconds': 'Maximum time (seconds)',
        'run_model': 'Run scheduling',
        'model_running': 'Model running...',
        'model_success': 'Model run successfully!',
        'model_error': 'Error running model',
        'invalid_date_range': 'Invalid date range',
        'end_before_start': 'End date must be after start date',
        'scheduling_for': 'Scheduling for',
        'days_total': 'days total',
        
        # NEW: Date-specific translations
        'date_input_method': 'Date input method',
        'select_individual_dates': 'Select individual dates',
        'specify_date_range': 'Specify date range',
        'individual_dates': 'Individual dates',
        'date_range': 'Date range',
        'from_date': 'From date',
        'to_date': 'To date',
        'selected_dates': 'Selected dates',
        
        # Messages
        'no_data': 'No data available',
        'data_saved': 'Data saved successfully',
        'data_loaded': 'Data loaded',
        'invalid_data': 'Invalid data',
        'required_field': 'This field is required',
        'constraint_added': 'Constraint added',
        'constraints_added': 'constraints added',
        'constraint_removed': 'Constraint removed',
        
        # File paths
        'data_files': 'Data files',
        'employees_file': 'Employees file',
        'shifts_file': 'Shifts file',
        'hard_constraints_file': 'Hard constraints file',
        'soft_constraints_file': 'Soft constraints file',
        
        # Help text
        'employee_id_help': 'Unique ID for the employee (e.g., EMP001)',
        'shift_id_help': 'Unique ID for the shift (e.g., DAY01)',
        'constraint_help': 'Hard constraints must be satisfied, soft constraints are preferred',
        'date_range_help': 'Choose start and end dates for the scheduling period',
        'date_input_help': 'Select specific dates or specify a date range',
        
        # New flexible parameter translations
        'targeting_method': 'Choose targeting method:',
        'specific_shift': 'Specific shift',
        'shift_category': 'Shift category',
        'multiple_categories': 'Multiple categories',
        'column_name': 'Column name',
        'column_value': 'Column value',
        'column_values': 'Column values',
        'column_name_help': 'Choose which column to match against',
        'column_value_help': 'The value to match in the selected column',
        'column_values_help': 'Comma-separated list of values',

        'historical_schedule': 'Historical Schedule',
        'use_historical_data': 'Use historical schedule data',
        'load_historical_schedule': 'Load historical schedule',
        'upload_method': 'Choose upload method',
        'upload_file': 'Upload file',
        'specify_path': 'Specify path',
        'choose_excel_file': 'Choose Excel file with historical schedule',
        'file_format_help': 'File should contain employee IDs as rows and dates as columns',
        'file_uploaded_successfully': 'File uploaded successfully',
        'file_preview': 'File preview',
        'historical_data_info': 'Historical data',
        'could_not_parse_dates': 'Could not parse date columns',
        'error_reading_file': 'Error reading file',
        'path_to_historical_file': 'Path to historical schedule file',
        'specify_full_path': 'Specify the full path to the Excel file',
        'file_found': 'File found',
        'file_not_found': 'File not found',
        'show_preview': 'Show preview',
        'format_help': 'Format help',
        'expected_file_format': 'Expected file format',
        'format_rules': 'Rules',
        'first_column_employee_ids': 'First column: Employee IDs',
        'other_columns_dates': 'Other columns: Dates in YYYY-MM-DD format',
        'cells_shift_ids': 'Cells: Shift IDs (e.g. \'DAG\', \'NAT\') or empty for days off',
        'extended_calendar_info': 'With historical data, the calendar will be extended to include both historical and future dates',
        'extended_calendar': 'Extended calendar',
        'historical_days': 'Historical days',
        'new_days': 'New days',
        'total_days': 'Total',
        'historical_integration_success': 'Historical schedule successfully integrated!',

        'file_input_method': 'File input method',
        'browse_for_file': 'Browse for file',
        'specify_file_path': 'Specify file path',
        'choose_file': 'Choose file',
        'file_selected': 'File selected',
        'upload_or_specify': 'Upload or specify',

        'app_title': 'Hospital Scheduling System',
        'app_subtitle': 'Manage staff, shifts, and constraints',
        'language': 'Language',
        'english': 'English',
        'danish': 'Dansk',
        'employees_tab': 'Employees',
        'shifts_tab': 'Shifts',
        'constraints_tab': 'Constraints',
        'run_model_tab': 'Run Model',

        'add_date': 'Add date',
        'add_column': 'Add column',

        'delete_column': 'Delete Column',
        'show_all_columns': 'Show all columns',
        'select_column_to_delete': 'Select column to delete', 
        'delete_column_help': 'Choose which column to permanently delete',
        'delete_warning': '⚠️ **Warning:** This action cannot be undone! The column and all its data will be permanently deleted.',
        'confirm_delete': '🗑️ Confirm Delete',
        'column_deleted_successfully': 'Column \'{}\' deleted successfully!',
        'no_columns_for_deletion': 'No columns available for deletion',
        'close': 'Close',

        'tools_tab': 'Tools',
        'rest_hours': "Minimum hours' rest",

        "add_shift_button": "Add shifts",

        "save_shifts_button": "Save shifts",
        "save_changes": "Save changes",
        "column_type": "Column type",

        "text": "Text",
        "number": "Number",
        "date": "Date",
        "time": "Time"
    }
}

def get_text(key, lang='da'):
    """Get translated text, with fallback to Danish if key not found."""
    return TRANSLATIONS.get(lang, {}).get(key, TRANSLATIONS['da'].get(key, key))

# =============================================================================
# DATE UTILITY FUNCTIONS
# =============================================================================

def get_next_month_range():
    """Get start and end dates for next month."""
    today = date.today()
    
    if today.month == 12:
        next_month_start = date(today.year + 1, 1, 1)
        next_month_end = date(today.year + 1, 2, 1) - timedelta(days=1)
    else:
        next_month_start = date(today.year, today.month + 1, 1)
        if today.month == 11:
            next_month_end = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            next_month_end = date(today.year, today.month + 2, 1) - timedelta(days=1)
    
    return next_month_start, next_month_end

def validate_date_range(start_date, end_date):
    """
    Validate that the date range is valid.
    
    Returns:
        tuple: (is_valid, error_message, num_days, description)
    """
    if end_date < start_date:
        return False, "End date must be on or after start date", 0, ""
    
    # Calculate total days (inclusive)
    num_days = (end_date - start_date).days + 1
    
    # Create a descriptive string
    if start_date.year == end_date.year:
        if start_date.month == end_date.month:
            description = f"{start_date.strftime('%B %Y')}, days {start_date.day}-{end_date.day}"
        else:
            description = f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
    else:
        description = f"{start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}"
    
    return True, "", num_days, description

# Add these functions after the existing utility functions
def save_file_paths(file_paths):
    """Save file paths to a JSON file for persistence."""
    try:
        config_path = "./.ui_config.json"
        with open(config_path, 'w') as f:
            json.dump(file_paths, f)
    except Exception as e:
        # Silently ignore save errors to avoid disrupting the UI
        pass

def load_saved_file_paths():
    """Load previously saved file paths from JSON file."""
    try:
        config_path = "./.ui_config.json"
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
    except Exception as e:
        # Return None if loading fails
        pass
    return None

# =============================================================================
# CONFIGURATION AND FILE PATHS
# =============================================================================

def get_file_paths():
    """Get file paths, preferring saved paths over defaults."""
    # Default paths
    base_path = "./"
    default_paths = {
        'employees': base_path + 'employees.xlsx',
        'shifts': base_path + 'shifts.xlsx',
        'hard_constraints': base_path + 'hard_constraints.xlsx',
        'soft_constraints': base_path + 'soft_constraints.xlsx'
    }
    
    # Try to load saved paths
    saved_paths = load_saved_file_paths()
    if saved_paths:
        # Use saved paths, but fall back to defaults for any missing keys
        for key in default_paths:
            if key not in saved_paths:
                saved_paths[key] = default_paths[key]
        return saved_paths
    
    return default_paths

def update_session_state_after_upload(config_key, temp_path, uploaded_file, lang):
    """
    Update session state DataFrames after file upload to refresh tabs immediately.
    This ensures all tabs show the new data without manual refresh.
    Includes check to prevent infinite rerun loops.
    """
    # Create a unique identifier for this uploaded file
    file_hash = hash((uploaded_file.name, uploaded_file.size, config_key))
    processed_files_key = f"processed_uploads_{config_key}"
    
    # Check if we've already processed this exact file upload
    if processed_files_key in st.session_state:
        if st.session_state[processed_files_key] == file_hash:
            # Already processed this file, don't rerun
            return
    
    try:
        if config_key == 'employees':
            # Load the uploaded employee data into session state
            new_employees_df = pd.read_excel(temp_path)
            new_employees_df = ensure_proper_employee_data_types(new_employees_df)
            st.session_state.employees_df = new_employees_df.copy()
            
        elif config_key == 'shifts':
            # Load the uploaded shift data into session state  
            new_shifts_df = pd.read_excel(temp_path)
            new_shifts_df = ensure_proper_shift_data_types(new_shifts_df)
            st.session_state.shifts_df = new_shifts_df.copy()
            
        elif config_key == 'hard_constraints':
            # Load the uploaded hard constraints into session state
            new_constraints_df = pd.read_excel(temp_path)
            st.session_state.hard_constraints_df = new_constraints_df.copy()
            
        elif config_key == 'soft_constraints':
            # Load the uploaded soft constraints into session state
            new_constraints_df = pd.read_excel(temp_path)
            st.session_state.soft_constraints_df = new_constraints_df.copy()
            
        # Mark this file as processed BEFORE calling rerun
        st.session_state[processed_files_key] = file_hash
        
        # Force UI refresh to update all tabs
        st.rerun()
        
    except Exception as e:
        st.warning(f"Could not update session state: {str(e)}")

# =============================================================================
# DATA LOADING AND SAVING FUNCTIONS (unchanged from original)
# =============================================================================

@st.cache_data
def load_employees(file_path):
    """Load employee data from Excel file with proper data type handling."""
    expected_columns = [
        'ID', 'nickname', 'title', 'shift_types'
    ]
    
    try:
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
            
            # Check if file is empty or doesn't have expected structure
            if df.empty or not any(col in df.columns for col in expected_columns):
                print(f"Empty or invalid employees file detected, creating proper structure")
                return create_empty_employees_df()
            
            # Ensure all expected columns exist
            for col in expected_columns:
                if col not in df.columns:
                    df[col] = pd.NA
            
            # FIXED: Explicitly convert text columns to string type to avoid float issues
            text_columns = ['ID', 'nickname', 'title', 'shift_types']
            for col in text_columns:
                if col in df.columns:
                    df[col] = df[col].astype('string')  # Use pandas string dtype
            
            # Ensure numeric columns are properly typed
            numeric_columns = ['weekly_hours', 'hourly_wage', 'hour_deficit', 
                             'current_night_shifts', 'current_evening_night_shifts']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Ensure date columns are properly formatted
            date_columns = ['norm_period_start', 'norm_period_end']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            return df
        else:
            # File doesn't exist, return empty dataframe with expected columns
            return create_empty_employees_df()
    except Exception as e:
        st.error(f"Error loading employees: {e}")
        return create_empty_employees_df()

def create_empty_employees_df():
    """Create empty employees dataframe with proper column types."""
    df = pd.DataFrame(columns=['ID', 'nickname', 'title', 'shift_types'])
    
    text_columns = ['ID', 'nickname', 'title', 'shift_types']
    for col in text_columns:
        df[col] = df[col].astype('string')
    
    return df

@st.cache_data
def load_shifts(file_path):
    """Load shift data from Excel file with proper data type handling."""
    expected_columns = ['shift_ID', 'start_time', 'end_time', 'shift_types']
    
    try:
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
            
            # Check if file is empty or doesn't have expected structure
            if df.empty or not any(col in df.columns for col in expected_columns):
                print(f"Empty or invalid shifts file detected, creating proper structure")
                return create_empty_shifts_df()
            
            # Ensure all expected columns exist
            for col in expected_columns:
                if col not in df.columns:
                    df[col] = pd.NA
            
            # FIXED: Explicitly convert text columns to string type to avoid float issues
            text_columns = ['shift_ID', 'shift_types']
            for col in text_columns:
                if col in df.columns:
                    df[col] = df[col].astype('string')  # Use pandas string dtype
            
            # Handle time columns formatting
            time_columns = ['start_time', 'end_time']
            for col in time_columns:
                if col in df.columns:
                    # Handle different possible time formats from Excel
                    if df[col].dtype == 'object':
                        # First try the format with seconds (HH:MM:SS)
                        try:
                            df[col] = pd.to_datetime(df[col], format='%H:%M:%S', errors='raise').dt.time
                        except (ValueError, TypeError):
                            # If that fails, try without seconds (HH:MM)
                            try:
                                df[col] = pd.to_datetime(df[col], format='%H:%M', errors='raise').dt.time
                            except (ValueError, TypeError):
                                # If both fail, try pandas' automatic parsing
                                df[col] = pd.to_datetime(df[col], errors='coerce').dt.time
                    elif pd.api.types.is_numeric_dtype(df[col]):
                        # Numeric format (Excel decimal time representation)
                        df[col] = pd.to_datetime(df[col], unit='D', origin='1900-01-01', errors='coerce').dt.time
                    elif pd.api.types.is_datetime64_any_dtype(df[col]):
                        # Already datetime, just extract time part
                        df[col] = df[col].dt.time
                        
            return df
        else:
            return create_empty_shifts_df()
    except Exception as e:
        st.error(f"Error loading shifts: {e}")
        return create_empty_shifts_df()

def create_empty_shifts_df():
    """Create empty shifts dataframe with proper column types."""
    df = pd.DataFrame(columns=['shift_ID', 'start_time', 'end_time', 'shift_types'])
    
    # FIXED: Set proper data types from the start to avoid float inference
    text_columns = ['shift_ID', 'shift_types']
    for col in text_columns:
        df[col] = df[col].astype('string')
    
    return df

def apply_shift_editor_changes_to_dataframe(base_df, editor_state):
    """
    Apply changes from st.data_editor to the shifts dataframe.
    
    Args:
        base_df: The original dataframe
        editor_state: The state dictionary from st.data_editor
        
    Returns:
        Updated dataframe with changes applied
    """
    result_df = base_df.copy()
    
    # Apply edited rows
    if 'edited_rows' in editor_state:
        for row_idx, changes in editor_state['edited_rows'].items():
            for col, new_value in changes.items():
                if row_idx < len(result_df):
                    result_df.iloc[row_idx, result_df.columns.get_loc(col)] = new_value
    
    # Apply added rows
    if 'added_rows' in editor_state:
        new_rows = []
        for new_row in editor_state['added_rows']:
            complete_row = {}
            for col in result_df.columns:
                complete_row[col] = new_row.get(col, pd.NA)
            new_rows.append(complete_row)
        
        if new_rows:
            new_rows_df = pd.DataFrame(new_rows)
            new_rows_df = ensure_proper_shift_data_types(new_rows_df)
            result_df = pd.concat([result_df, new_rows_df], ignore_index=True)
    
    # Apply deleted rows
    if 'deleted_rows' in editor_state:
        rows_to_delete = sorted(editor_state['deleted_rows'], reverse=True)
        for row_idx in rows_to_delete:
            if row_idx < len(result_df):
                result_df = result_df.drop(result_df.index[row_idx]).reset_index(drop=True)
    
    # Ensure proper data types after all changes
    result_df = ensure_proper_shift_data_types(result_df)
    
    return result_df

def ensure_proper_shift_data_types(df):
    """Ensure shift DataFrame has proper data types to avoid Streamlit compatibility issues."""
    if df.empty:
        return df
    
    df = df.copy()
    
    # Convert text columns to string type
    text_columns = ['shift_ID', 'shift_types', 'shift_category']
    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].astype('object')
            mask = pd.isna(df[col]) | (df[col] == 'nan') | (df[col] == '<NA>') | (df[col] is None)
            df.loc[mask, col] = ''
            df[col] = df[col].astype(str)
    
    # Handle time columns more robustly
    time_columns = ['start_time', 'end_time']
    for col in time_columns:
        if col in df.columns:
            # Convert each value individually to handle mixed types
            new_values = []
            for value in df[col]:
                if pd.isna(value):
                    new_values.append(pd.NaT)
                elif isinstance(value, str):
                    try:
                        # Try parsing as time string
                        if ':' in value:
                            try:
                                # Try HH:MM:SS format first
                                time_obj = pd.to_datetime(value, format='%H:%M:%S').time()
                                new_values.append(time_obj)
                            except ValueError:
                                try:
                                    # Fall back to HH:MM format
                                    time_obj = pd.to_datetime(value, format='%H:%M').time()
                                    new_values.append(time_obj)
                                except ValueError:
                                    # If both fail, try pandas' automatic parsing
                                    try:
                                        time_obj = pd.to_datetime(value, errors='coerce').time()
                                        new_values.append(time_obj if pd.notna(time_obj) else pd.NaT)
                                    except:
                                        new_values.append(pd.NaT)
                        else:
                            new_values.append(pd.NaT)
                    except:
                        new_values.append(pd.NaT)
                elif hasattr(value, 'hour'):  # Already a time object
                    new_values.append(value)
                else:
                    new_values.append(pd.NaT)
            
            df[col] = new_values
    
    return df

@st.cache_data
def load_constraints(file_path):
    """Load constraint data from Excel file with proper data type handling."""
    try:
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
            
            # For constraints, we can accept empty files
            if df.empty:
                return pd.DataFrame(columns=['constraint_type'])
            
            # Ensure proper data types for constraint columns
            df = ensure_proper_constraint_data_types(df)
            
            return df
        else:
            return pd.DataFrame(columns=['constraint_type'])
    except Exception as e:
        st.error(f"Error loading constraints: {e}")
        return pd.DataFrame(columns=['constraint_type'])

def ensure_proper_constraint_data_types(df):
    """Ensure constraint DataFrame has proper data types to avoid Streamlit compatibility issues."""
    if df.empty:
        return df
    
    df = df.copy()
    
    # Convert text columns to string type
    text_columns = ['constraint_type', 'ID', 'shift_ID', 'category', 'column_name', 'column_value', 'column_values']
    for col in text_columns:
        if col in df.columns:
            # Convert to object type first to handle mixed types
            df[col] = df[col].astype('object')
            # Replace NaN/null values with empty strings
            mask = pd.isna(df[col]) | (df[col] == 'nan') | (df[col] == '<NA>') | (df[col] is None)
            df.loc[mask, col] = ''
            # Convert to string
            df[col] = df[col].astype(str)
    
    # Convert date columns that might be in constraints
    date_columns = ['day', 'start_day', 'end_day']
    for col in date_columns:
        if col in df.columns:
            # Keep date strings as strings - don't convert to datetime objects for constraints
            df[col] = df[col].astype('object')
            mask = pd.isna(df[col]) | (df[col] == 'nan') | (df[col] == '<NA>') | (df[col] is None)
            df.loc[mask, col] = ''
            df[col] = df[col].astype(str)
    
    # Handle time columns that might be in constraints
    time_columns = ['time']
    for col in time_columns:
        if col in df.columns:
            # Keep time values as strings for constraints
            df[col] = df[col].astype('object')
            mask = pd.isna(df[col])
            df.loc[mask, col] = ''
            df[col] = df[col].astype(str)
    
    # Ensure numeric columns are properly typed
    numeric_columns = ['weight', 'max_hours', 'min_rest_hours', 'max_shifts', 'shifts_count', 
                       'week_number', 'check_days', 'window_days', 'days_between']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

def create_empty_employees_df():
    """Create empty employees dataframe with proper column types."""
    df = pd.DataFrame(columns=[
        'ID', 'nickname', 'title', 'weekly_hours', 'shift_types', 
        'hourly_wage', 'norm_period_start', 'norm_period_end',
        'hour_deficit', 'current_night_shifts', 'current_evening_night_shifts'
    ])
    # Set proper data types
    df['norm_period_start'] = pd.to_datetime(df['norm_period_start'])
    df['norm_period_end'] = pd.to_datetime(df['norm_period_end'])
    return df

def save_dataframe(df, file_path, success_message):
    """Save dataframe to Excel file with error handling."""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df.to_excel(file_path, index=False)
        st.success(success_message)
        # Clear cache to reload fresh data
        load_employees.clear()
        load_shifts.clear()
        load_constraints.clear()  # This is important for constraints
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

# =============================================================================
# CONSTRAINT LOADING FUNCTIONS - DYNAMIC LOADING FROM ACTUAL CONSTRAINT CLASSES
# =============================================================================

def load_available_constraints():
    """
    Dynamically load available constraints from the actual constraint loader classes.
    
    This function imports the constraint modules and extracts the constraint types
    directly from their constraint_types dictionaries. This ensures the UI automatically
    stays in sync with constraint definitions without requiring manual updates.
    
    Returns:
        dict: Dictionary with 'hard' and 'soft' keys containing constraint type mappings
    """
    try:
        # Import the constraint modules - these contain the actual constraint definitions
        from core.hard_constraints import HardConstraintLoader
        from core.soft_constraints import SoftConstraintLoader
        
        # Create instances to access their constraint_types dictionaries
        # We use dummy paths since we only need access to the constraint type definitions
        hard_loader = HardConstraintLoader("dummy_path")
        soft_loader = SoftConstraintLoader("dummy_path")
        
        return {
            'hard': hard_loader.constraint_types,
            'soft': soft_loader.constraint_types
        }
    
    except Exception as e:
        st.error(f"Error loading constraint types: {e}")
        return {'hard': {}, 'soft': {}}

# List of constraints to hide from the UI - you can modify this list as needed
# These are typically system-level constraints that should always be active
HIDDEN_CONSTRAINTS = {}

def filter_constraints_for_ui(constraint_types, constraint_category):
    """
    Filter out constraints that should be hidden from the UI.
    
    This allows you to hide system-level or automatically-applied constraints
    while still showing user-configurable constraints in the interface.
    
    Args:
        constraint_types: Dictionary of constraint types from loader
        constraint_category: 'hard' or 'soft' constraint category
        
    Returns:
        dict: Filtered constraint types suitable for UI display
    """
    filtered = {}
    for name, (class_obj, required_params) in constraint_types.items():
        if name not in HIDDEN_CONSTRAINTS:
            filtered[name] = (class_obj, required_params)
    return filtered

# =============================================================================
# EMPLOYEE MANAGEMENT TAB (unchanged from original)
# =============================================================================

DEFAULT_EMPLOYEE_COLUMNS = [
    'ID', 
    'nickname', 
    'title', 
    'shift_types'
]

def show_employees_tab(lang):
    """Display the employee management interface with improved column management."""
    
    # Get file path
    file_paths = get_file_paths()
    employees_file = file_paths['employees']
    
    # Load current data
    employees_df = load_employees(employees_file)
    
    # Better session state initialization and management
    if 'employees_df' not in st.session_state or st.session_state.employees_df.empty:
        st.session_state.employees_df = employees_df.copy()
        st.session_state.employees_df = ensure_proper_employee_data_types(st.session_state.employees_df)
    
    # Initialize show_all_columns if not exists
    if 'show_all_columns' not in st.session_state:
        st.session_state.show_all_columns = False

    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button(get_text('add', lang) + " " + get_text('employees_tab', lang), key="add_employee_button"):
            st.session_state.show_add_employee = True
            st.rerun()
    
    with col2:
        if st.button(get_text('save_changes', lang), key="save_employees_button"):
            if 'employees_editor' in st.session_state:
                edited_data = st.session_state.employees_editor
                if 'edited_rows' in edited_data or 'added_rows' in edited_data or 'deleted_rows' in edited_data:
                    # Apply edits to the base dataframe
                    updated_df = apply_editor_changes_to_dataframe(
                        st.session_state.employees_df.copy(), 
                        edited_data
                    )
                    
                    if save_dataframe(updated_df, employees_file, get_text('data_saved', lang)):
                        # Update session state with the saved data
                        st.session_state.employees_df = updated_df.copy()
                        st.rerun()
                else:
                    st.info("No changes to save" if lang == 'en' else "Ingen ændringer at gemme")
            else:
                st.warning("No editor data found" if lang == 'en' else "Ingen editor data fundet")
    
    with col3:
        # FIXED: Add a button to discard unsaved changes
        if st.button("Discard Changes" if lang == 'en' else "Fortryd Ændringer"):
            st.session_state.employees_df = load_employees(employees_file)
            st.session_state.employees_df = ensure_proper_employee_data_types(st.session_state.employees_df)
            # Clear the editor state
            if 'employees_editor' in st.session_state:
                del st.session_state.employees_editor
            st.success("Changes discarded" if lang == 'en' else "Ændringer fortrudt")
            st.rerun()
    
    with col4:
        if st.button(get_text('add_column', lang)):
            st.session_state.show_add_column = True
            st.rerun()
    
    with col5:
        # NEW: Delete column button
        if st.button("🗑️ " + ("Delete Column" if lang == 'en' else "Slet Kolonne")):
            st.session_state.show_delete_column = True
            st.rerun()

    # Initialize the checkbox state if it doesn't exist
    if 'show_all_columns_checkbox' not in st.session_state:
        st.session_state.show_all_columns_checkbox = st.session_state.get('show_all_columns', False)

    # Use the checkbox with key, let Streamlit manage the state
    show_all_columns = st.checkbox(
        "Show all columns" if lang == 'en' else "Vis alle kolonner",
        key="show_all_columns_checkbox"
    )

    # Update your session state for other parts of the code that reference it
    st.session_state.show_all_columns = show_all_columns

    # NEW: Delete column form
    if getattr(st.session_state, 'show_delete_column', False):
        show_delete_column_form(lang)

    # Add column form (updated without default value)
    if getattr(st.session_state, 'show_add_column', False):
        show_add_column_form(lang)
                
    # Add employee form (only show if flag is set)
    if getattr(st.session_state, 'show_add_employee', False):
        show_add_employee_form(lang)
    
    # Display and edit existing employees
    if not st.session_state.employees_df.empty and 'ID' in st.session_state.employees_df.columns:
        
        # UPDATED: Configure the data editor with proper column configurations and filtering
        column_config = get_employee_column_config(lang)

        # NEW: Determine which columns to display based on show_all_columns setting
        if st.session_state.show_all_columns:
            # Create consistent ordering: default columns first, then additional columns
            display_columns = []
            
            # Add default columns first (in their defined order)
            for col in DEFAULT_EMPLOYEE_COLUMNS:
                if col in st.session_state.employees_df.columns:
                    display_columns.append(col)
            
            # Add any additional columns that aren't in the default list
            for col in st.session_state.employees_df.columns:
                if col not in DEFAULT_EMPLOYEE_COLUMNS and col not in display_columns:
                    display_columns.append(col)
        else:
            # Only show default columns that exist in the dataframe
            display_columns = [col for col in DEFAULT_EMPLOYEE_COLUMNS if col in st.session_state.employees_df.columns]
        
        # FIXED: Don't process data types again here - use session state directly
        display_df = st.session_state.employees_df[display_columns].copy()

        # FIXED: Ensure text columns are strings without converting NaN to empty string unnecessarily
        for col in ['ID', 'nickname', 'title', 'shift_types']:
            if col in display_df.columns:
                # Only convert non-null values to string, preserve existing valid strings
                display_df[col] = display_df[col].astype('object')  # Use object dtype to preserve mixed types
                # Replace only actual NaN values, not existing strings
                mask = pd.isna(display_df[col]) | (display_df[col] == 'nan') | (display_df[col] == '<NA>')
                display_df.loc[mask, col] = ''
        
        try:
            # REMOVED: The automatic session state update that was causing issues
            edited_df = st.data_editor(
                display_df,
                column_config={k: v for k, v in column_config.items() if k in display_columns},
                num_rows="dynamic",
                width='stretch',
                key="employees_editor",
                hide_index=True
            )
            
        except Exception as e:
            st.error(f"Error in data editor: {e}")
            st.info("Try refreshing the data if you continue to have issues.")
    else:
        st.info(get_text('no_data', lang))

def get_employee_column_config(lang):
    """Get column configuration including custom columns."""
    
    # Base column configuration
    column_config = {
        "ID": st.column_config.TextColumn(
            get_text('employee_id_required', lang),
            help=get_text('employee_id_help', lang),
            required=True,
            max_chars=50
        ),
        "nickname": st.column_config.TextColumn(
            get_text('nickname', lang),
            max_chars=100,
            help="Click in cell and type to edit" if lang == 'en' else "Klik i celle og skriv for at redigere"
        ),
        "title": st.column_config.TextColumn(
            get_text('title', lang),
            max_chars=100,
            help="Click in cell and type to edit" if lang == 'en' else "Klik i celle og skriv for at redigere"
        ),
        "shift_types": st.column_config.TextColumn(
            get_text('shift_types', lang),
            help="Comma-separated list" if lang == 'en' else "Kommasepareret liste"
        )
    }
    
    # Add custom columns if they exist
    if 'custom_columns' in st.session_state:
        for col_name, col_info in st.session_state.custom_columns.items():
            if col_info['type'] == 'number':
                column_config[col_name] = st.column_config.NumberColumn(
                    col_info['display_name'],
                    step=0.1
                )
            elif col_info['type'] == 'date':
                column_config[col_name] = st.column_config.DateColumn(
                    col_info['display_name']
                )
            elif col_info['type'] == 'time':
                column_config[col_name] = st.column_config.TimeColumn(
                    col_info['display_name']
                )
            else:  # text
                column_config[col_name] = st.column_config.TextColumn(
                    col_info['display_name'],
                    max_chars=200
                )
    
    return column_config

def show_add_column_form(lang):
    """Display form to add a new column to the employee data"""
    with st.expander(get_text('add_column', lang), expanded=True):
        with st.form("add_column_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                column_name = st.text_input(
                    get_text('column_name',lang),
                    help="Enter a unique column name" if lang == 'en' else "Indtast et unikt kolonnenavn"
                )
            
            with col2:
                column_type = st.selectbox(
                    get_text('column_type',lang),
                    options=["text", "number", "date", "time"],
                    format_func=lambda x: {
                        "text": get_text('text',lang),
                        "number": get_text('number',lang), 
                        "date": get_text('date',lang),
                        "time": get_text('time',lang)
                    }[x]
                )
            
            col_submit, col_cancel = st.columns(2)
            
            with col_submit:
                if st.form_submit_button(get_text('add_column', lang)):
                    if column_name and column_name not in st.session_state.employees_df.columns:
                        # Add the new column to the dataframe (with empty default value)
                        add_column_to_employees(column_name, column_type, "", lang)
                        st.session_state.show_add_column = False
                        st.rerun()
                    elif not column_name:
                        st.error("Column name is required" if lang == 'en' else "Kolonnenavn er påkrævet")
                    else:
                        st.error("Column already exists" if lang == 'en' else "Kolonne findes allerede")
            
            with col_cancel:
                if st.form_submit_button(get_text('cancel', lang)):
                    st.session_state.show_add_column = False
                    st.rerun()

def show_delete_column_form(lang):
    """NEW: Display form to delete a column from the employee data."""
    with st.expander("🗑️ " + ("Delete Column" if lang == 'en' else "Slet Kolonne"), expanded=True):
        with st.form("delete_column_form"):
            # Get list of columns that can be deleted (exclude required columns)
            protected_columns = ['ID']  # Add other protected columns as needed
            available_columns = [col for col in st.session_state.employees_df.columns if col not in protected_columns]
            
            if not available_columns:
                st.warning("No columns available for deletion" if lang == 'en' else "Ingen kolonner tilgængelige til sletning")
                if st.form_submit_button("Close" if lang == 'en' else "Luk"):
                    st.session_state.show_delete_column = False
                    st.rerun()
                return
            
            column_to_delete = st.selectbox(
                "Select column to delete" if lang == 'en' else "Vælg kolonne til sletning",
                options=available_columns,
                help="Choose which column to permanently delete" if lang == 'en' else "Vælg hvilken kolonne der skal slettes permanent"
            )
            
            st.warning(
                "⚠️ **Warning:** This action cannot be undone! The column and all its data will be permanently deleted."
                if lang == 'en' else
                "⚠️ **Advarsel:** Denne handling kan ikke fortrydes! Kolonnen og alle dens data vil blive permanent slettet."
            )
            
            col_submit, col_cancel = st.columns(2)
            
            with col_submit:
                if st.form_submit_button(
                    "🗑️ Confirm Delete" if lang == 'en' else "🗑️ Bekræft Sletning",
                    type="primary"
                ):
                    if column_to_delete:
                        # Remove column from dataframe
                        st.session_state.employees_df = st.session_state.employees_df.drop(columns=[column_to_delete])
                        
                        # Remove from custom columns metadata if it exists
                        if 'custom_columns' in st.session_state and column_to_delete in st.session_state.custom_columns:
                            del st.session_state.custom_columns[column_to_delete]
                        
                        st.session_state.show_delete_column = False
                        st.success(
                            f"Column '{column_to_delete}' deleted successfully!" if lang == 'en' else
                            f"Kolonne '{column_to_delete}' slettet succesfuldt!"
                        )
                        st.rerun()
            
            with col_cancel:
                if st.form_submit_button("Cancel" if lang == 'en' else "Annuller"):
                    st.session_state.show_delete_column = False
                    st.rerun()

def add_column_to_employees(column_name, column_type, default_value, lang):
    """Add a new column to the employees dataframe with proper type handling (UPDATED: always empty default)."""
    
    # UPDATED: Always use empty default value regardless of input
    if column_type == "number":
        default_val = pd.NA
    elif column_type == "date":
        default_val = pd.NaT
    elif column_type == "time":
        default_val = pd.NaT
    else:  # text
        default_val = ""
    
    # Add column to dataframe
    st.session_state.employees_df[column_name] = default_val
    
    # Store column metadata for proper display configuration
    if 'custom_columns' not in st.session_state:
        st.session_state.custom_columns = {}
    
    st.session_state.custom_columns[column_name] = {
        'type': column_type,
        'display_name': column_name,
        'default_value': default_val
    }
    
    st.success(f"Column '{column_name}' added successfully!" if lang == 'en' 
              else f"Kolonne '{column_name}' tilføjet succesfuldt!")

def apply_editor_changes_to_dataframe(base_df, editor_state):
    """
    Apply changes from st.data_editor to the base dataframe.
    
    Args:
        base_df: The original dataframe
        editor_state: The state dictionary from st.data_editor
        
    Returns:
        Updated dataframe with changes applied
    """
    result_df = base_df.copy()
    
    # Apply edited rows
    if 'edited_rows' in editor_state:
        for row_idx, changes in editor_state['edited_rows'].items():
            for col, new_value in changes.items():
                if row_idx < len(result_df):
                    result_df.iloc[row_idx, result_df.columns.get_loc(col)] = new_value
    
    # Apply added rows
    if 'added_rows' in editor_state:
        new_rows = []
        for new_row in editor_state['added_rows']:
            # Ensure the new row has all required columns
            complete_row = {}
            for col in result_df.columns:
                complete_row[col] = new_row.get(col, pd.NA)
            new_rows.append(complete_row)
        
        if new_rows:
            new_rows_df = pd.DataFrame(new_rows)
            # Ensure proper data types for new rows
            new_rows_df = ensure_proper_employee_data_types(new_rows_df)
            result_df = pd.concat([result_df, new_rows_df], ignore_index=True)
    
    # Apply deleted rows
    if 'deleted_rows' in editor_state:
        # Sort in reverse order to delete from the end first
        rows_to_delete = sorted(editor_state['deleted_rows'], reverse=True)
        for row_idx in rows_to_delete:
            if row_idx < len(result_df):
                result_df = result_df.drop(result_df.index[row_idx]).reset_index(drop=True)
    
    # Ensure proper data types after all changes
    result_df = ensure_proper_employee_data_types(result_df)
    
    return result_df

def ensure_proper_employee_data_types(df):
    """Ensure employee DataFrame has proper data types to avoid Streamlit compatibility issues."""
    if df.empty:
        return df
    
    df = df.copy()
    
    # FIXED: More careful handling of text columns to avoid losing user input
    text_columns = ['ID', 'nickname', 'title', 'shift_types']
    for col in text_columns:
        if col in df.columns:
            # Convert to object type first to handle mixed types
            df[col] = df[col].astype('object')
            # Only replace actual NaN/None values, not existing strings
            mask = pd.isna(df[col]) | (df[col] == 'nan') | (df[col] == '<NA>') | (df[col] is None)
            df.loc[mask, col] = ''
            # Ensure remaining values are strings
            df[col] = df[col].astype(str)
    
    # Ensure numeric columns are properly typed
    numeric_columns = ['weekly_hours', 'hourly_wage', 'hour_deficit', 
                       'current_night_shifts', 'current_evening_night_shifts']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Ensure date columns are datetime
    date_columns = ['norm_period_start', 'norm_period_end']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    return df

def show_add_employee_form(lang):
    """
    Show the form for adding a new employee with dynamic field generation.
    Makes ID, nickname, title, and shift_types mandatory while allowing 
    optional input for all other columns in the dataset.
    """
    st.subheader("Add New Employee" if lang == 'en' else "Tilføj Ny Medarbejder")
    
    with st.container(border=True):
        with st.form("add_employee_form"):
            st.write("**Enter employee details:**" if lang == 'en' else "**Indtast medarbejderoplysninger:**")
            
            # --- MANDATORY FIELDS SECTION ---
            st.write("### " + ("Required Fields" if lang == 'en' else "Påkrævede Felter"))
            
            # Create columns for mandatory fields
            col1, col2 = st.columns(2)
            
            with col1:
                employee_id = st.text_input(
                    get_text('employee_id_required', lang),
                    help=get_text('employee_id_help', lang),
                    placeholder="e.g., EMP001",
                    key="mandatory_employee_id"
                )
                
                nickname = st.text_input(
                    get_text('nickname', lang) + " *",
                    placeholder="Employee's preferred name",
                    key="mandatory_nickname"
                )
            
            with col2:
                title = st.text_input(
                    get_text('title', lang) + " *",
                    placeholder="Job title or position",
                    key="mandatory_title"
                )
                
                shift_types = st.text_input(
                    get_text('shift_types', lang) + " *",
                    help="Comma-separated list" if lang == 'en' else "Kommasepareret liste",
                    placeholder="e.g., DAG,NAT,AFTEN",
                    key="mandatory_shift_types"
                )
            
            # --- OPTIONAL FIELDS SECTION ---
            st.write("### " + ("Optional Fields" if lang == 'en' else "Valgfrie Felter"))
            
            # Get all columns from the dataframe excluding mandatory ones
            mandatory_columns = {'ID', 'nickname', 'title', 'shift_types'}
            
            # Get reference dataframe structure
            if hasattr(st.session_state, 'employees_df') and not st.session_state.employees_df.empty:
                reference_df = st.session_state.employees_df
            else:
                # Create reference from the default structure
                reference_df = create_empty_employees_df()
                # Add all known columns
                additional_columns = {
                    'weekly_hours': 0.0,
                    'hourly_wage': 0.0, 
                    'norm_period_start': pd.NaT,
                    'norm_period_end': pd.NaT,
                    'hour_deficit': pd.NA,
                    'current_night_shifts': pd.NA,
                    'current_evening_night_shifts': pd.NA
                }
                for col, default_val in additional_columns.items():
                    if col not in reference_df.columns:
                        reference_df[col] = default_val
            
            # Get optional columns
            optional_columns = [col for col in reference_df.columns if col not in mandatory_columns]
            
            # Dictionary to store optional field values
            optional_values = {}
            
            if optional_columns:
                # Create expandable section for optional fields
                with st.expander("📋 " + ("Show Optional Fields" if lang == 'en' else "Vis Valgfrie Felter"), expanded=False):
                    
                    # Group columns by type for better organization
                    text_columns = []
                    numeric_columns = []
                    date_columns = []
                    time_columns = []
                    other_columns = []
                    
                    for col in optional_columns:
                        if col in reference_df.columns:
                            dtype = reference_df[col].dtype
                            
                            # Check if it's a custom column with metadata
                            if hasattr(st.session_state, 'custom_columns') and col in st.session_state.custom_columns:
                                custom_type = st.session_state.custom_columns[col]['type']
                                if custom_type == 'number':
                                    numeric_columns.append(col)
                                elif custom_type == 'date':
                                    date_columns.append(col)
                                elif custom_type == 'time':
                                    time_columns.append(col)
                                else:
                                    text_columns.append(col)
                            else:
                                # Determine type from pandas dtype
                                if pd.api.types.is_numeric_dtype(dtype):
                                    numeric_columns.append(col)
                                elif pd.api.types.is_datetime64_any_dtype(dtype):
                                    date_columns.append(col)
                                else:
                                    text_columns.append(col)
                        else:
                            other_columns.append(col)
                    
                    # Create form fields based on column types
                    if text_columns:
                        st.write("**" + ("Text Fields" if lang == 'en' else "Tekstfelter") + "**")
                        cols = st.columns(min(len(text_columns), 3))
                        for i, col in enumerate(text_columns):
                            with cols[i % len(cols)]:
                                display_name = get_text(col, lang) if col in get_text('', lang) else col.replace('_', ' ').title()
                                optional_values[col] = st.text_input(
                                    display_name,
                                    key=f"optional_{col}",
                                    help=f"Enter {col.replace('_', ' ')}"
                                )
                    
                    if numeric_columns:
                        st.write("**" + ("Numeric Fields" if lang == 'en' else "Numeriske Felter") + "**")
                        cols = st.columns(min(len(numeric_columns), 3))
                        for i, col in enumerate(numeric_columns):
                            with cols[i % len(cols)]:
                                display_name = get_text(col, lang) if col in get_text('', lang) else col.replace('_', ' ').title()
                                
                                # Set appropriate parameters based on column
                                if 'hours' in col.lower():
                                    min_val, max_val, step = 0.0, 60.0, 0.5
                                elif 'wage' in col.lower():
                                    min_val, max_val, step = 0.0, 1000.0, 10.0
                                elif 'deficit' in col.lower():
                                    min_val, max_val, step = -100.0, 100.0, 0.5
                                elif 'shifts' in col.lower():
                                    min_val, max_val, step = 0.0, 50.0, 1.0
                                else:
                                    min_val, max_val, step = 0.0, 1000.0, 0.1
                                
                                optional_values[col] = st.number_input(
                                    display_name,
                                    min_value=min_val,
                                    max_value=max_val,
                                    step=step,
                                    value=None,
                                    key=f"optional_{col}",
                                    help=f"Enter {col.replace('_', ' ')}"
                                )
                    
                    if date_columns:
                        st.write("**" + ("Date Fields" if lang == 'en' else "Datofelter") + "**")
                        cols = st.columns(min(len(date_columns), 2))
                        for i, col in enumerate(date_columns):
                            with cols[i % len(cols)]:
                                display_name = get_text(col, lang) if col in get_text('', lang) else col.replace('_', ' ').title()
                                optional_values[col] = st.date_input(
                                    display_name,
                                    value=None,
                                    key=f"optional_{col}",
                                    help=f"Select {col.replace('_', ' ')}"
                                )
                    
                    if time_columns:
                        st.write("**" + ("Time Fields" if lang == 'en' else "Tidsfelter") + "**")
                        cols = st.columns(min(len(time_columns), 2))
                        for i, col in enumerate(time_columns):
                            with cols[i % len(cols)]:
                                display_name = get_text(col, lang) if col in get_text('', lang) else col.replace('_', ' ').title()
                                optional_values[col] = st.time_input(
                                    display_name,
                                    value=None,
                                    key=f"optional_{col}",
                                    help=f"Select {col.replace('_', ' ')}"
                                )
                    
                    if other_columns:
                        st.write("**" + ("Other Fields" if lang == 'en' else "Andre Felter") + "**")
                        for col in other_columns:
                            display_name = col.replace('_', ' ').title()
                            optional_values[col] = st.text_input(
                                display_name,
                                key=f"optional_{col}",
                                help=f"Enter {col.replace('_', ' ')}"
                            )
            else:
                st.info("No additional fields available" if lang == 'en' else "Ingen yderligere felter tilgængelige")
            
            # --- FORM SUBMISSION ---
            st.divider()
            col_submit, col_cancel = st.columns(2)
            
            with col_submit:
                submitted = st.form_submit_button(
                    "✅ " + get_text('add', lang), 
                    type="primary",
                    use_container_width=True
                )
            
            with col_cancel:
                cancelled = st.form_submit_button(
                    "❌ " + get_text('cancel', lang),
                    use_container_width=True
                )
            
            # Handle form submission
            if cancelled:
                st.session_state.show_add_employee = False
                st.rerun()
            
            if submitted:
                # Validate mandatory fields
                errors = []
                if not employee_id.strip():
                    errors.append("Employee ID is required" if lang == 'en' else "Medarbejder-ID er påkrævet")
                if not nickname.strip():
                    errors.append("Nickname is required" if lang == 'en' else "Kaldenavn er påkrævet")
                if not title.strip():
                    errors.append("Title is required" if lang == 'en' else "Titel er påkrævet")
                if not shift_types.strip():
                    errors.append("Shift types are required" if lang == 'en' else "Vagttyper er påkrævet")
                
                # Check for duplicate ID
                existing_ids = []
                if (hasattr(st.session_state, 'employees_df') and 
                    not st.session_state.employees_df.empty and 
                    'ID' in st.session_state.employees_df.columns):
                    existing_ids = st.session_state.employees_df['ID'].astype(str).tolist()
                
                if employee_id.strip() in existing_ids:
                    errors.append("Employee ID already exists" if lang == 'en' else "Medarbejder-ID findes allerede")
                
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    # Create new employee dictionary with all columns
                    new_employee = {
                        'ID': str(employee_id.strip()),
                        'nickname': str(nickname.strip()),
                        'title': str(title.strip()),
                        'shift_types': str(shift_types.strip())
                    }
                    
                    # Add optional fields with proper type conversion
                    for col, value in optional_values.items():
                        if col in reference_df.columns:
                            dtype = reference_df[col].dtype
                            
                            if value is not None and value != "":
                                # Check if it's a custom column
                                if hasattr(st.session_state, 'custom_columns') and col in st.session_state.custom_columns:
                                    custom_type = st.session_state.custom_columns[col]['type']
                                    if custom_type == 'number':
                                        new_employee[col] = float(value) if value is not None else pd.NA
                                    elif custom_type == 'date':
                                        new_employee[col] = pd.to_datetime(value) if value else pd.NaT
                                    elif custom_type == 'time':
                                        new_employee[col] = pd.to_datetime(str(value)) if value else pd.NaT
                                    else:
                                        new_employee[col] = str(value) if value else ""
                                else:
                                    # Handle based on pandas dtype
                                    if pd.api.types.is_numeric_dtype(dtype):
                                        new_employee[col] = float(value) if value is not None else pd.NA
                                    elif pd.api.types.is_datetime64_any_dtype(dtype):
                                        new_employee[col] = pd.to_datetime(value) if value else pd.NaT
                                    else:
                                        new_employee[col] = str(value) if value else ""
                            else:
                                # Set appropriate empty value based on type
                                if pd.api.types.is_numeric_dtype(dtype):
                                    new_employee[col] = pd.NA
                                elif pd.api.types.is_datetime64_any_dtype(dtype):
                                    new_employee[col] = pd.NaT
                                else:
                                    new_employee[col] = ""
                    
                    # Ensure all expected columns exist in the new employee record
                    for col in reference_df.columns:
                        if col not in new_employee:
                            dtype = reference_df[col].dtype
                            if pd.api.types.is_numeric_dtype(dtype):
                                new_employee[col] = pd.NA
                            elif pd.api.types.is_datetime64_any_dtype(dtype):
                                new_employee[col] = pd.NaT
                            else:
                                new_employee[col] = ""
                    
                    # Create DataFrame and add to session state
                    new_df = pd.DataFrame([new_employee])
                    new_df = ensure_proper_employee_data_types(new_df)
                    
                    st.session_state.employees_df = pd.concat([
                        st.session_state.employees_df,
                        new_df
                    ], ignore_index=True)
                    
                    st.session_state.show_add_employee = False
                    st.success("Employee added successfully!" if lang == 'en' else "Medarbejder tilføjet succesfuldt!")
                    st.rerun()
# =============================================================================
# SHIFT MANAGEMENT TAB (unchanged from original)
# =============================================================================

DEFAULT_SHIFT_COLUMNS = [
    'shift_ID', 
    'start_time', 
    'end_time', 
    'shift_types',
]

def show_shifts_tab(lang):
    """Display the shift management interface with improved column management (ENHANCED VERSION)."""
    
    # Get file path
    file_paths = get_file_paths()
    shifts_file = file_paths['shifts']
    
    # Load current data
    shifts_df = load_shifts(shifts_file)
    
    # Better session state initialization and management
    if 'shifts_df' not in st.session_state or st.session_state.shifts_df.empty:
        st.session_state.shifts_df = shifts_df.copy()
        st.session_state.shifts_df = ensure_proper_shift_data_types(st.session_state.shifts_df)
    
    # Initialize show_all_columns for shifts if not exists
    if 'show_all_shift_columns' not in st.session_state:
        st.session_state.show_all_shift_columns = False

    # Enhanced action buttons - NOW WITH 5 BUTTONS LIKE EMPLOYEE TAB
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button(get_text('add_shift_button', lang), key="add_shift_button"):
            st.session_state.show_add_shift = True
            st.rerun()
    
    with col2:
        if st.button(get_text('save_shifts_button', lang), key="save_shifts_button"):
            if 'shifts_editor' in st.session_state:
                edited_data = st.session_state.shifts_editor
                if 'edited_rows' in edited_data or 'added_rows' in edited_data or 'deleted_rows' in edited_data:
                    # Apply edits to the base dataframe
                    updated_df = apply_shift_editor_changes_to_dataframe(
                        st.session_state.shifts_df.copy(), 
                        edited_data
                    )
                    
                    if save_dataframe(updated_df, shifts_file, get_text('data_saved', lang)):
                        # Update session state with the saved data
                        st.session_state.shifts_df = updated_df.copy()
                        st.rerun()
                else:
                    st.info("No changes to save" if lang == 'en' else "Ingen ændringer at gemme")
            else:
                st.warning("No editor data found" if lang == 'en' else "Ingen editor data fundet")
    
    with col3:
        # NEW: Add a button to discard unsaved changes
        if st.button("↩️ Discard Changes" if lang == 'en' else "↩️ Fortryd Ændringer", key="discard_shifts_button"):
            st.session_state.shifts_df = load_shifts(shifts_file)
            st.session_state.shifts_df = ensure_proper_shift_data_types(st.session_state.shifts_df)
            # Clear the editor state
            if 'shifts_editor' in st.session_state:
                del st.session_state.shifts_editor
            st.success("Changes discarded" if lang == 'en' else "Ændringer fortryd")
            st.rerun()
    
    with col4:
        # NEW: Add column button
        if st.button(get_text('add_column', lang), key="add_shift_column_button"):
            st.session_state.show_add_shift_column = True
            st.rerun()
    
    with col5:
        # NEW: Delete column button
        if st.button("🗑️ " + ("Delete Column" if lang == 'en' else "Slet Kolonne"), key="delete_shift_column_button"):
            st.session_state.show_delete_shift_column = True
            st.rerun()

    # NEW: Initialize the checkbox state if it doesn't exist
    if 'show_all_shift_columns_checkbox' not in st.session_state:
        st.session_state.show_all_shift_columns_checkbox = st.session_state.get('show_all_shift_columns', False)

    # NEW: Use the checkbox with key, let Streamlit manage the state
    show_all_shift_columns = st.checkbox(
        "Show all columns" if lang == 'en' else "Vis alle kolonner",
        key="show_all_shift_columns_checkbox"
    )

    # NEW: Update your session state for other parts of the code that reference it
    st.session_state.show_all_shift_columns = show_all_shift_columns

    # NEW: Delete column form
    if getattr(st.session_state, 'show_delete_shift_column', False):
        show_delete_shift_column_form(lang)

    # NEW: Add column form
    if getattr(st.session_state, 'show_add_shift_column', False):
        show_add_shift_column_form(lang)
                
    # Add shift form (only show if flag is set)
    if getattr(st.session_state, 'show_add_shift', False):
        show_add_shift_form(lang)
    
    # Display and edit existing shifts
    if not st.session_state.shifts_df.empty and 'shift_ID' in st.session_state.shifts_df.columns:
        
        # NEW: Show a warning about unsaved changes
        st.info(
            "💡 **Tip:** Edit the data below directly. Remember to click 'Save Changes' to persist your edits!"
            if lang == 'en' else
            "💡 **Tip:** Rediger dataene direkte nedenfor. Husk at klikke 'Gem Ændringer' for at gemme dine redigeringer!"
        )
        
        # NEW: Configure the data editor with proper column configurations and filtering
        column_config = get_shift_column_config(lang)

        # NEW: Determine which columns to display based on show_all_shift_columns setting
        if st.session_state.show_all_shift_columns:
            # Create consistent ordering: default columns first, then additional columns
            display_columns = []
            
            # Add default columns first (in their defined order)
            for col in DEFAULT_SHIFT_COLUMNS:
                if col in st.session_state.shifts_df.columns:
                    display_columns.append(col)
            
            # Add any additional columns that aren't in the default list
            for col in st.session_state.shifts_df.columns:
                if col not in DEFAULT_SHIFT_COLUMNS and col not in display_columns:
                    display_columns.append(col)
        else:
            # Only show default columns that exist in the dataframe
            display_columns = [col for col in DEFAULT_SHIFT_COLUMNS if col in st.session_state.shifts_df.columns]


        # NEW: Don't process data types again here - use session state directly
        display_df = st.session_state.shifts_df[display_columns].copy()

        # NEW: Ensure text columns are strings without converting NaN to empty string unnecessarily
        for col in ['shift_ID', 'shift_types', 'shift_category']:
            if col in display_df.columns:
                # Only convert non-null values to string, preserve existing valid strings
                display_df[col] = display_df[col].astype('object')  # Use object dtype to preserve mixed types
                # Replace only actual NaN values, not existing strings
                mask = pd.isna(display_df[col]) | (display_df[col] == 'nan') | (display_df[col] == '<NA>')
                display_df.loc[mask, col] = ''
        
        try:
            # NEW: The enhanced data editor with column filtering
            edited_df = st.data_editor(
                display_df,
                column_config={k: v for k, v in column_config.items() if k in display_columns},
                num_rows="dynamic",
                width="stretch",
                key="shifts_editor",
                hide_index=True
            )
            
        except Exception as e:
            st.error(f"Error in data editor: {e}")
            st.info("Try refreshing the data if you continue to have issues.")
    else:
        st.info(get_text('no_data', lang))

def get_shift_column_config(lang):
    """Get column configuration including custom columns for shifts."""
    
    # Base column configuration for shifts
    column_config = {
        "shift_ID": st.column_config.TextColumn(
            get_text('shift_id_required', lang),
            help=get_text('shift_id_help', lang),
            required=True,
            max_chars=50
        ),
        "start_time": st.column_config.TimeColumn(
            get_text('start_time', lang),
            help="Click in cell to edit time" if lang == 'en' else "Klik i celle for at redigere tid"
        ),
        "end_time": st.column_config.TimeColumn(
            get_text('end_time', lang),
            help="Click in cell to edit time" if lang == 'en' else "Klik i celle for at redigere tid"
        ),
        "shift_types": st.column_config.TextColumn(
            get_text('shift_types', lang),
            help="Comma-separated list" if lang == 'en' else "Kommasepareret liste",
            max_chars=200
        ),
        "shift_category": st.column_config.TextColumn(
            get_text('shift_category', lang),
            help="Click in cell and type to edit" if lang == 'en' else "Klik i celle og skriv for at redigere",
            max_chars=100
        )
    }
    
    # NEW: Add custom columns if they exist for shifts
    if 'custom_shift_columns' in st.session_state:
        for col_name, col_info in st.session_state.custom_shift_columns.items():
            if col_info['type'] == 'number':
                column_config[col_name] = st.column_config.NumberColumn(
                    col_info['display_name'],
                    step=0.1
                )
            elif col_info['type'] == 'date':
                column_config[col_name] = st.column_config.DateColumn(
                    col_info['display_name']
                )
            elif col_info['type'] == 'time':
                column_config[col_name] = st.column_config.TimeColumn(
                    col_info['display_name']
                )
            else:  # text
                column_config[col_name] = st.column_config.TextColumn(
                    col_info['display_name'],
                    max_chars=200
                )
    
    return column_config

# NEW: Display form to add a new column to the shift data
def show_add_shift_column_form(lang):
    """Display form to add a new column to the shift data."""
    
    with st.expander("➕ " + ("Add New Column" if lang == 'en' else "Tilføj Ny Kolonne"), expanded=True):
        with st.form("add_shift_column_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                column_name = st.text_input(
                    "Column Name" if lang == 'en' else "Kolonnenavn",
                    help="Enter a unique column name" if lang == 'en' else "Indtast et unikt kolonnenavn"
                )
                
            
            with col2:
                column_type = st.selectbox(
                    "Column Type" if lang == 'en' else "Kolonnetype",
                    options=["text", "number", "date", "time"],
                    format_func=lambda x: {
                        "text": "Text" if lang == 'en' else "Tekst",
                        "number": "Number" if lang == 'en' else "Nummer", 
                        "date": "Date" if lang == 'en' else "Dato",
                        "time": "Time" if lang == 'en' else "Klokkeslet"
                    }[x]
                )
            
            col_submit, col_cancel = st.columns(2)
            
            with col_submit:
                if st.form_submit_button("Add Column" if lang == 'en' else "Tilføj Kolonne"):
                    if column_name and column_name not in st.session_state.shifts_df.columns:
                        # Add the new column to the dataframe
                        add_column_to_shifts(column_name, column_type, "", lang)
                        st.session_state.show_add_shift_column = False
                        st.rerun()
                    elif not column_name:
                        st.error("Column name is required" if lang == 'en' else "Kolonnenavn er påkrævet")
                    else:
                        st.error("Column already exists" if lang == 'en' else "Kolonne findes allerede")
            
            with col_cancel:
                if st.form_submit_button("Cancel" if lang == 'en' else "Annuller"):
                    st.session_state.show_add_shift_column = False
                    st.rerun()

# NEW: Display form to delete a column from the shift data
def show_delete_shift_column_form(lang):
    """Display form to delete a column from the shift data."""
    
    with st.expander("🗑️ " + ("Delete Column" if lang == 'en' else "Slet Kolonne"), expanded=True):
        with st.form("delete_shift_column_form"):
            
            # Get available columns (excluding required ones)
            required_columns = ['shift_ID']  # shift_ID is required, others can be deleted
            available_columns = [col for col in st.session_state.shifts_df.columns 
                               if col not in required_columns]
            
            if not available_columns:
                st.warning("No columns available for deletion" if lang == 'en' 
                          else "Ingen kolonner tilgængelige til sletning")
                if st.form_submit_button("Close" if lang == 'en' else "Luk"):
                    st.session_state.show_delete_shift_column = False
                    st.rerun()
                return
            
            column_to_delete = st.selectbox(
                "Select column to delete" if lang == 'en' else "Vælg kolonne til sletning",
                options=available_columns,
                help="Choose which column to permanently delete" if lang == 'en' 
                     else "Vælg hvilken kolonne der skal slettes permanent"
            )
            
            st.markdown(
                "⚠️ **Warning:** This action cannot be undone! The column and all its data will be permanently deleted."
                if lang == 'en' else
                "⚠️ **Advarsel:** Denne handling kan ikke fortrydes! Kolonnen og alle dens data vil blive permanent slettet."
            )
            
            col_delete, col_cancel = st.columns(2)
            
            with col_delete:
                if st.form_submit_button("🗑️ Confirm Delete" if lang == 'en' else "🗑️ Bekræft Sletning"):
                    if column_to_delete:
                        # Remove column from dataframe
                        st.session_state.shifts_df = st.session_state.shifts_df.drop(columns=[column_to_delete])
                        
                        # Remove from custom columns metadata if it exists
                        if 'custom_shift_columns' in st.session_state and column_to_delete in st.session_state.custom_shift_columns:
                            del st.session_state.custom_shift_columns[column_to_delete]
                        
                        st.session_state.show_delete_shift_column = False
                        st.success(
                            f"Column '{column_to_delete}' deleted successfully!"
                            if lang == 'en' else
                            f"Kolonne '{column_to_delete}' slettet succesfuldt!"
                        )
                        st.rerun()
            
            with col_cancel:
                if st.form_submit_button("Cancel" if lang == 'en' else "Annuller"):
                    st.session_state.show_delete_shift_column = False
                    st.rerun()

# NEW: Add a new column to the shifts dataframe with proper type handling
def add_column_to_shifts(column_name, column_type, default_value, lang):
    """Add a new column to the shifts dataframe with proper type handling."""
    
    # Always use empty default value regardless of input
    if column_type == "number":
        default_val = pd.NA
    elif column_type == "date":
        default_val = pd.NaT
    elif column_type == "time":
        default_val = pd.NaT
    else:  # text
        default_val = ""
    
    # Add column to dataframe
    st.session_state.shifts_df[column_name] = default_val
    
    # Store column metadata for proper display configuration
    if 'custom_shift_columns' not in st.session_state:
        st.session_state.custom_shift_columns = {}
    
    st.session_state.custom_shift_columns[column_name] = {
        'type': column_type,
        'display_name': column_name,
        'default_value': default_val
    }
    
    st.success(f"Column '{column_name}' added successfully!" if lang == 'en' 
              else f"Kolonne '{column_name}' tilføjet succesfuldt!")

def show_add_shift_form(lang):
    """Show the form for adding a new shift with safe column access."""
    st.subheader(get_text('add_shift_button', lang))

    with st.container(border=True):
        with st.form("add_shift_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                shift_id = st.text_input(
                    get_text('shift_id_required', lang),
                    help=get_text('shift_id_help', lang)
                )
                start_time = st.time_input(
                    get_text('start_time', lang),
                    value=None
                )
                end_time = st.time_input(
                    get_text('end_time', lang),
                    value=None
                )
            
            with col2:
                shift_types = st.text_input(
                    get_text('shift_types', lang),
                    help="Kommasepareret liste" if lang == 'da' else "Comma-separated list"
                )
                shift_category = st.text_input(get_text('shift_category', lang))
            
            col_submit, col_cancel = st.columns(2)
            with col_submit:
                submitted = st.form_submit_button(
                    "✅ " + get_text('add', lang), 
                    type="primary",
                    width='stretch',
                    # No key needed for form_submit_button - they're automatically unique within forms
                )
            with col_cancel:
                cancelled = st.form_submit_button(
                    "❌ " + get_text('cancel', lang),
                    width='stretch',
                    # No key needed for form_submit_button - they're automatically unique within forms
                )
            
            if cancelled:
                st.session_state.show_add_shift = False
                st.rerun()
            
            if submitted:
                if not shift_id.strip():
                    st.error(get_text('required_field', lang))
                else:
                    # Safe check for existing shift ID
                    existing_ids = []
                    if not st.session_state.shifts_df.empty and 'shift_ID' in st.session_state.shifts_df.columns:
                        existing_ids = st.session_state.shifts_df['shift_ID'].values.tolist()
                    
                    if shift_id in existing_ids:
                        st.error("Vagt ID findes allerede" if lang == 'da' else "Shift ID already exists")
                    else:
                        # Create new shift row
                        new_shift = {
                            'shift_ID': shift_id.strip(),
                            'start_time': start_time,
                            'end_time': end_time,
                            'shift_types': shift_types.strip() if shift_types else "",
                            'shift_category': shift_category.strip() if shift_category else ""
                        }
                        
                        # Add to dataframe
                        st.session_state.shifts_df = pd.concat([
                            st.session_state.shifts_df,
                            pd.DataFrame([new_shift])
                        ], ignore_index=True)
                        
                        st.session_state.show_add_shift = False
                        st.success("Vagt tilføjet" if lang == 'da' else "Shift added")
                        st.rerun()

# =============================================================================
# CONSTRAINT MANAGEMENT TAB - ENHANCED WITH DYNAMIC LOADING AND DATE SUPPORT
# =============================================================================

class ConstraintUIConfig:
    """Centralized configuration for constraint UI elements and validation rules."""
    def __init__(self, lang='da'):
        self.lang = lang
    
        # Validation rules for parameters
        VALIDATION_RULES = {
            'weight': lambda x: x > 0,
            'max_hours': lambda x: x >= 0,
            'min_rest_hours': lambda x: x >= 0,
            'max_shifts': lambda x: x >= 0,
            'shifts_count': lambda x: x >= 0,
            'ID': lambda x: len(x) > 0 if isinstance(x, list) else x is not None,
            'shift_ID': lambda x: len(x) > 0 if isinstance(x, list) else x is not None,
        }
        
        # Error messages for validation failures
        VALIDATION_MESSAGES = {
            'weight': 'Weight must be positive',
            'max_hours': 'Max hours must be non-negative',
            'min_rest_hours': 'Min rest hours must be non-negative', 
            'max_shifts': 'Max shifts must be non-negative',
            'shifts_count': 'Shifts count must be non-negative',
            'ID': 'At least one employee must be selected',
            'shift_ID': 'At least one shift must be selected',
        }
        def get_enhanced_parameter_widgets(lang):
            """Enhanced parameter widgets with better date handling."""
            return {
                'weight': {
                    'type': 'number_input',
                    'label': 'Weight',
                    'min_value': 0.1,
                    'max_value': 100.0,
                    'value': 1.0,
                    'help': 'Weight for soft constraint (higher = more important)'
                },
                'ID': {
                    'type': 'multiselect',
                    'label': 'Employee(s)',
                    'source': 'employees',
                    'help': 'Select one or more employees'
                },
                'shift_ID': {
                    'type': 'multiselect', 
                    'label': 'Shift(s)',
                    'source': 'shifts',
                    'help': 'Select one or more shifts'
                },
                'day': {
                    'type': 'date_multiselect',
                    'label': 'Date(s)',
                    'help': 'Select dates using various methods'  # FIXED: Updated help text
                },
                'start_day': {
                    'type': 'date_input',
                    'label': 'Start Date',
                    'help': 'Start date for date range'
                },
                'end_day': {
                    'type': 'date_input', 
                    'label': 'End Date',
                    'help': 'End date for date range'
                },
                'time': {
                    'type': 'time_input',
                    'label': 'Time',
                    'help': 'Select time (HH:MM format)'
                },
                'max_hours': {
                    'type': 'number_input',
                    'label': 'Maximum Hours',
                    'min_value': 0,
                    'max_value': 168,
                    'help': 'Maximum number of hours per week'
                },
                'min_rest_hours': {
                    'type': 'number_input',
                    'label': (get_text('rest_hours', lang)), 
                    'min_value': 0,
                    'max_value': 48,
                    'value': 11,
                    'help': 'Minimum rest hours between shifts'
                },
                'max_shifts': {
                    'type': 'number_input',
                    'label': 'Maximum Shifts',
                    'min_value': 0,
                    'max_value': 31,
                    'help': 'Maximum number of shifts in period'
                },
                'shifts_count': {
                    'type': 'number_input',
                    'label': 'Number of Shifts',
                    'min_value': 0,
                    'max_value': 31,
                    'help': 'Exact number of shifts required'
                },
                'column_name': {
                    'type': 'selectbox',
                    'label': 'Column Name',
                    'source': 'shift_columns',
                    'help': 'Select column to filter by'
                },
                'column_value': {
                    'type': 'text_input',
                    'label': 'Column Value',
                    'help': 'Value to match in selected column'
                },
                'column_values': {
                    'type': 'text_input',
                    'label': 'Column Values',
                    'help': 'Comma-separated list of values to match'
                },
                'category': {
                    'type': 'text_input',
                    'label': 'Shift Category',
                    'help': 'Name of shift category (e.g., "Night", "Day", "Emergency")'
                },
                'days_between': {
                    'type': 'number_input',
                    'label': 'Days Between',
                    'min_value': 1,
                    'max_value': 14,
                    'value': 2,
                    'help': 'Minimum days between shifts of same category'
                },
                'window_days': {
                    'type': 'number_input',
                    'label': 'Window Days',
                    'min_value': 2,
                    'max_value': 14,
                    'value': 7,
                    'help': 'Number of days in rolling window'
                },
                'week_number': {
                    'type': 'number_input',
                    'label': 'ISO Week Number',
                    'min_value': 1,
                    'max_value': 53,
                    'help': 'ISO week number (1-53)'
                },
                'check_days': {
                    'type': 'number_input',
                    'label': 'Check Days',
                    'min_value': 1,
                    'max_value': 14,
                    'value': 7,
                    'help': 'Number of days from start to check'
                }
            }
        # Parameter widget configurations
        #self.PARAMETER_WIDGETS = get_enhanced_parameter_widgets(lang)


# =============================================================================
# CONSTRAINT MANAGEMENT CLASSES
# =============================================================================

class ConstraintParameterHandler:
    """Handles all constraint parameter input creation, validation, and processing."""
    
    def __init__(self, lang: str = 'da'):
        self.lang = lang
        self.config = ConstraintUIConfig()
    
    def render_parameters(self, required_params: Union[List, Dict], constraint_name: str, 
                         employees_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Unified parameter rendering method that handles all parameter types.
        
        FIXED: Date parameters are now handled outside the form to allow proper interaction.
        """
        parameters = {}
        date_params = []
        
        # Handle flexible parameters (method selection)
        if isinstance(required_params, dict):
            method_params = self._handle_flexible_parameters(required_params, constraint_name)
        else:
            method_params = required_params.copy() if required_params else []
        
        if not method_params:
            st.info(
                "Denne begrænsning kræver ingen parametre" if self.lang == 'da' 
                else "This constraint requires no parameters"
            )
            return {}
        
        # Separate date parameters from others
        for param in method_params:
            param_config = self._get_parameter_display_config(param, constraint_name)
            if param_config.get('type') in ['date_multiselect', 'date_input']:
                date_params.append(param)
        
        # Handle date parameters OUTSIDE the form
        if date_params:
            st.subheader(("Dato parametre" if self.lang == 'da' else "Date Parameters"))
            for param in date_params:
                method = st.selectbox(
                    "Date input method:",
                    ["Single date", "Date range", "Multiple dates"],
                    key=f"method_{constraint_name}_{param}")
                parameters[param] = self._create_date_parameter_outside_form(param, constraint_name, method)
        
        # Handle non-date parameters INSIDE the form
        non_date_params = [p for p in method_params if p not in date_params]
        
        if non_date_params:
            for param in non_date_params:
                parameters[param] = self._create_parameter_input(param, constraint_name, employees_df)
        
        return parameters
    
    def _handle_flexible_parameters(self, param_alternatives: Dict, constraint_name: str) -> List[str]:
        """Handle flexible parameter method selection."""
        # Create user-friendly labels
        method_labels = {
            'specific': 'Specific targeting' if self.lang == 'en' else 'Specifik målretning',
            'specific_shift': 'Specific targeting' if self.lang == 'en' else 'Angiv specifik vagt',
            'specific_employee': 'Specific targeting' if self.lang == 'en' else 'Angiv specifik medarbejder',
            'category': 'Category targeting' if self.lang == 'en' else 'Angiv kolonne',
            'multi_category': 'Multiple categories' if self.lang == 'en' else 'Flere kategorier'
        }
        
        # Create display options
        display_options = []
        method_mapping = {}
        
        for key in param_alternatives.keys():
            display_label = method_labels.get(key, key.replace('_', ' ').title())
            display_options.append(display_label)
            method_mapping[display_label] = key
        
        # Method selection
        selected_method_label = st.radio(
            "Targeting method:" if self.lang == 'en' else "Målretningsmetode:",
            display_options,
            key=f"method_{constraint_name}"
        )
        
        selected_method = method_mapping[selected_method_label]
        return param_alternatives[selected_method]
    
    def _create_parameter_input(self, param: str, constraint_name: str, employees_df: pd.DataFrame) -> Any:
        """Create appropriate input widget for a parameter with constraint-specific configuration support."""
        
        # NEW: Use the new method to get parameter configuration
        config = self._get_parameter_display_config(param, constraint_name)
        
        widget_type = config.get('type', 'text_input')
        key = f"{constraint_name}_{param}"
        
        # Special handling for column_name - enhanced to show all available columns
        if param == 'column_name':
            return self._create_column_name_selectbox(constraint_name, employees_df, config)
        
        # Dynamic column_value input based on selected column_name
        if param == 'column_value':
            return self._create_dynamic_column_value_input(constraint_name, employees_df, config)
        
        # Handle different widget types based on config
        if widget_type == 'multiselect':
            if config.get('source') == 'employees':
                options = employees_df['ID'].tolist() if not employees_df.empty else []
                return st.multiselect(
                    config.get('label', param.replace('_', ' ').title()),
                    options,
                    help=config.get('help'),
                    key=key
                )
            elif config.get('source') == 'shifts':
                file_paths = get_file_paths()
                shifts_df = load_shifts(file_paths['shifts'])
                options = shifts_df['shift_ID'].tolist() if not shifts_df.empty else []
                return st.multiselect(
                    config.get('label', param.replace('_', ' ').title()),
                    options,
                    help=config.get('help'),
                    key=key
                )
        
        elif widget_type == 'selectbox':
            if config.get('source') == 'employees':
                options = [""] + employees_df['ID'].tolist() if not employees_df.empty else [""]
                return st.selectbox(
                    config.get('label', param.replace('_', ' ').title()),
                    options,
                    help=config.get('help'),
                    key=key
                )
            elif config.get('source') == 'shifts':
                file_paths = get_file_paths()
                shifts_df = load_shifts(file_paths['shifts'])
                options = [""] + shifts_df['shift_ID'].tolist() if not shifts_df.empty else [""]
                return st.selectbox(
                    config.get('label', param.replace('_', ' ').title()),
                    options,
                    help=config.get('help'),
                    key=key
                )
        
        elif widget_type == 'number_input':
            return st.number_input(
                config.get('label', param.replace('_', ' ').title()),
                min_value=config.get('min_value', 0),
                max_value=config.get('max_value', 1000),
                value=config.get('value', 0),
                help=config.get('help'),
                key=key
            )
        
        elif widget_type == 'time_input':
            return st.time_input(
                config.get('label', param.replace('_', ' ').title()),
                help=config.get('help'),
                key=key
            )
        
        else:  # Default to text_input
            return st.text_input(
                config.get('label', param.replace('_', ' ').title()),
                help=config.get('help', f'Enter value for {param}'),
                key=key
            )
    
    # NEW METHOD: Add this method to get parameter display configuration
    def _get_parameter_display_config(self, param: str, constraint_name: str) -> dict:
        """
        Get parameter display configuration from constraint class or fallback to defaults.
        Priority order:
        1. parameter_display_config class variable from constraint
        2. get_parameter_config_override() method (backward compatibility)
        3. Default to parameter name as label
        """
        # Try to get constraint class
        constraint_class = self._get_constraint_class(constraint_name)
        
        if constraint_class:
            # 1. Check for parameter_display_config class variable
            if hasattr(constraint_class, 'parameter_display_config'):
                display_config = getattr(constraint_class, 'parameter_display_config')
                if isinstance(display_config, dict) and param in display_config:
                    return display_config[param]
            
            # 2. Fallback to existing get_parameter_config_override method
            if hasattr(constraint_class, 'get_parameter_config_override'):
                try:
                    override_config = constraint_class.get_parameter_config_override()
                    if param in override_config:
                        return override_config[param]
                except Exception:
                    pass
        
        # 3. Default: create basic config with parameter name as label
        return {
            'type': 'text_input',
            'label': param.replace('_', ' ').title(),
            'help': f'Enter value for {param}'
        }
    
    def _get_constraint_class(self, constraint_name: str):
        """Get the constraint class object."""
        try:
            from core.hard_constraints import HardConstraintLoader
            from core.soft_constraints import SoftConstraintLoader
            
            hard_loader = HardConstraintLoader("dummy")
            soft_loader = SoftConstraintLoader("dummy")
            
            hard_types = hard_loader.constraint_types
            soft_types = getattr(soft_loader, 'constraint_types', {})
            
            if constraint_name in hard_types:
                return hard_types[constraint_name][0]
            elif constraint_name in soft_types:
                return soft_types[constraint_name][0]
            
            return None
        except Exception:
            return None

    def _create_enhanced_column_name_input(self, constraint_name: str, employees_df: pd.DataFrame, config: dict) -> Any:
        """
        Enhanced column_name input that shows columns from both employees and shifts dataframes.
        """
        key = f"{constraint_name}_column_name"
        
        # Get columns from employees dataframe
        employee_columns = []
        if not employees_df.empty:
            employee_columns = [(col, 'employees') for col in employees_df.columns if col != 'ID']
        
        # Get columns from shifts dataframe
        shift_columns = []
        try:
            file_paths = get_file_paths()
            shifts_df = load_shifts(file_paths['shifts'])
            if not shifts_df.empty:
                shift_columns = [(col, 'shifts') for col in shifts_df.columns if col != 'shift_ID']
        except Exception:
            shift_columns = []
        
        # Combine all columns
        all_columns = employee_columns + shift_columns
        
        if not all_columns:
            return st.text_input(
                config.get('label', 'Column Name'),
                help="No columns found - enter column name manually",
                key=key
            )
        
        # Create display options with source indication when needed
        display_options = [""]
        column_mapping = {"": ""}
        
        # Track columns we've seen to handle duplicates
        seen_columns = {}
        
        for col_name, source in all_columns:
            if col_name in seen_columns:
                # Handle duplicate column names by adding source suffix
                display_name_1 = f"{col_name} ({seen_columns[col_name]})"
                display_name_2 = f"{col_name} ({source})"
                
                # Update the first occurrence
                if col_name in column_mapping.values():
                    for k, v in column_mapping.items():
                        if v == col_name:
                            column_mapping[display_name_1] = col_name
                            display_options[display_options.index(k)] = display_name_1
                            del column_mapping[k]
                            break
                
                # Add the second occurrence
                display_options.append(display_name_2)
                column_mapping[display_name_2] = col_name
            else:
                # First time seeing this column name
                display_options.append(col_name)
                column_mapping[col_name] = col_name
                seen_columns[col_name] = source
        
        # Create the selectbox
        selected_display = st.selectbox(
            config.get('label', 'Column Name'),
            display_options,
            help=config.get('help', 'Select column to filter by'),
            key=key
        )
        
        # Return the actual column name (without source suffix)
        return column_mapping.get(selected_display, selected_display)

    def _create_dynamic_column_value_input(self, constraint_name: str, employees_df: pd.DataFrame, config: dict) -> Any:
        """
        Create a dynamic column_value input that shows a dropdown of unique values
        from the selected column_name.
        """
        key = f"{constraint_name}_column_value"
        column_name_key = f"{constraint_name}_column_name"
        
        # Get the currently selected column name
        selected_column = st.session_state.get(column_name_key, "")
        
        # If no column is selected, show disabled text input with helpful message
        if not selected_column or selected_column == "":
            return st.text_input(
                config.get('label', 'Column Value'),
                help="First select a column name above",
                key=key,
                disabled=True,
                placeholder="Select a column name first..."
            )
        
        # Get unique values from the selected column
        unique_values = self._get_unique_column_values(selected_column, employees_df)
        
        # If no unique values found or very few values, show text input with suggestions
        if not unique_values:
            return st.text_input(
                config.get('label', f'Value for "{selected_column}"'),
                help=f'No values found in column "{selected_column}" - enter value manually',
                key=key
            )
        
        # If there are many unique values (>50), show text input with expander showing options
        if len(unique_values) > 50:
            with st.expander(f"📋 Available values in '{selected_column}' ({len(unique_values)} total)"):
                st.write(", ".join(sorted(unique_values)[:20]))
                if len(unique_values) > 20:
                    st.write(f"... and {len(unique_values) - 20} more")
            
            return st.text_input(
                config.get('label', f'Value for "{selected_column}"'),
                help=f'Enter value from column "{selected_column}" (see available values above)',
                key=key
            )
        
        # Show dropdown with unique values (for reasonable number of options)
        sorted_values = sorted([str(val) for val in unique_values])
        
        return st.selectbox(
            config.get('label', f'Value for "{selected_column}"'),
            [""] + sorted_values,
            help=config.get('help', f'Select a value from column "{selected_column}"'),
            key=key
        )

    def _get_unique_column_values(self, column_name: str, employees_df: pd.DataFrame) -> list:
        """
        Get unique values from the specified column across both employees and shifts dataframes.
        """
        unique_values = set()
        
        try:
            # Check employees dataframe
            if not employees_df.empty and column_name in employees_df.columns:
                emp_values = employees_df[column_name].dropna().unique()
                unique_values.update(str(val).strip() for val in emp_values if str(val).strip())
            
            # Check shifts dataframe
            try:
                file_paths = get_file_paths()
                shifts_df = load_shifts(file_paths['shifts'])
                
                if not shifts_df.empty and column_name in shifts_df.columns:
                    shift_values = shifts_df[column_name].dropna().unique()
                    unique_values.update(str(val).strip() for val in shift_values if str(val).strip())
            except Exception:
                pass
                
        except Exception as e:
            print(f"Error getting unique values for column '{column_name}': {e}")
        
        return list(unique_values)

    # Usage tip: Make sure to call st.rerun() or use session state callbacks 
    # to refresh the column_value widget when column_name changes
    def _handle_column_name_change(self, constraint_name: str):
        """
        Handle column_name changes to reset column_value selection.
        Call this when column_name widget value changes.
        """
        column_value_key = f"{constraint_name}_column_value"
        if column_value_key in st.session_state:
            del st.session_state[column_value_key]

    def _create_date_parameter_outside_form(self, param: str, constraint_name: str, method: str) -> Any:
        """
        STREAMLINED SOLUTION: Enhanced date parameter creation with automatic state management.
        
        Uses unique, method-specific keys to avoid session state conflicts.
        Much cleaner than manual session state clearing.
        """
        
        # Create method-specific container to ensure clean separation
        with st.container():
            st.write(f"**{param.replace('_', ' ').title()} - {method} Mode:**")
            
            # Use method-specific keys to avoid conflicts
            base_key = f"{constraint_name}_{param}_{method.replace(' ', '_')}"
            
            if method == "Single date":
                selected_date = st.date_input(
                    "Select date:" if self.lang == 'en' else "Vælg dato:",
                    key=f"{base_key}_single",
                    help="Choose a single date" if self.lang == 'en' else "Vælg en enkelt dato"
                )
                
                if selected_date:
                    return [selected_date.strftime('%Y-%m-%d')]
                else:
                    return []
            
            elif method == "Date range":
                col1, col2 = st.columns(2)
                
                with col1:
                    start_date = st.date_input(
                        "Start date:" if self.lang == 'en' else "Start dato:",
                        key=f"{base_key}_start",
                        help="Select start date" if self.lang == 'en' else "Vælg startdato"
                    )
                
                with col2:
                    end_date = st.date_input(
                        "End date:" if self.lang == 'en' else "Slut dato:",
                        key=f"{base_key}_end",
                        help="Select end date" if self.lang == 'en' else "Vælg slutdato"
                    )
                
                if start_date and end_date:
                    if end_date >= start_date:
                        # Generate date range
                        dates = []
                        current = start_date
                        while current <= end_date:
                            dates.append(current.strftime('%Y-%m-%d'))
                            current += timedelta(days=1)
                        
                        st.success(f"✅ {len(dates)} dates selected: {dates[0]} to {dates[-1]}" 
                                if self.lang == 'en' else 
                                f"✅ {len(dates)} datoer valgt: {dates[0]} til {dates[-1]}")
                        return dates
                    else:
                        st.error("End date must be after start date" if self.lang == 'en' 
                                else "Slutdato skal være efter startdato")
                        return []
                else:
                    if start_date or end_date:
                        st.info("Please select both start and end dates" if self.lang == 'en' 
                            else "Vælg både start- og slutdato")
                    return []
            
            elif method == "Multiple dates":
                # Method 1: Text area for manual entry
                st.write("**Option 1: Text Entry**" if self.lang == 'en' else "**Mulighed 1: Tekst indtastning**")
                
                text_input = st.text_area(
                    "Enter dates (YYYY-MM-DD, one per line):" if self.lang == 'en' 
                    else "Indtast datoer (YYYY-MM-DD, en per linje):",
                    key=f"{base_key}_text",
                    placeholder="2025-07-15\n2025-07-20\n2025-07-25",
                    help="Enter each date on a new line" if self.lang == 'en' 
                        else "Indtast hver dato på en ny linje"
                )
                
                dates_from_text = []
                if text_input.strip():
                    try:
                        for line in text_input.strip().split('\n'):
                            line = line.strip()
                            if line:
                                # Validate date format
                                datetime.strptime(line, '%Y-%m-%d')
                                dates_from_text.append(line)
                        
                        if dates_from_text:
                            st.success(f"✅ {len(dates_from_text)} dates from text" 
                                    if self.lang == 'en' else 
                                    f"✅ {len(dates_from_text)} datoer fra tekst")
                            
                    except ValueError:
                        st.error("Invalid date format. Use YYYY-MM-DD" if self.lang == 'en' 
                                else "Ugyldigt datoformat. Brug YYYY-MM-DD")
                        dates_from_text = []
                
                # Method 2: Interactive date picker
                st.write("**Option 2: Interactive Selection**" if self.lang == 'en' 
                        else "**Mulighed 2: Interaktiv udvælgelse**")
                
                # Initialize session state for dynamic dates
                dynamic_dates_key = f"{base_key}_dynamic_list"
                if dynamic_dates_key not in st.session_state:
                    st.session_state[dynamic_dates_key] = [None]
                
                dates_from_picker = []
                dynamic_dates = st.session_state[dynamic_dates_key]
                
                for i, date_value in enumerate(dynamic_dates):
                    col1, col2, col3 = st.columns([6, 1, 1])
                    
                    with col1:
                        selected_date = st.date_input(
                            f"Date {i+1}:" if self.lang == 'en' else f"Dato {i+1}:",
                            value=date_value,
                            key=f"{base_key}_picker_{i}"
                        )
                        
                        if selected_date:
                            dates_from_picker.append(selected_date.strftime('%Y-%m-%d'))
                            # Update session state
                            st.session_state[dynamic_dates_key][i] = selected_date
                    
                    with col2:
                        # Add button (only on last row)
                        if i == len(dynamic_dates) - 1:
                            if st.button("➕", key=f"{base_key}_add_{i}", 
                                    help="Add another date" if self.lang == 'en' 
                                            else "Tilføj endnu en dato"):
                                st.session_state[dynamic_dates_key].append(None)
                                st.rerun()
                    
                    with col3:
                        # Remove button (only if more than one)
                        if len(dynamic_dates) > 1:
                            if st.button("❌", key=f"{base_key}_remove_{i}",
                                    help="Remove this date" if self.lang == 'en' 
                                            else "Fjern denne dato"):
                                st.session_state[dynamic_dates_key].pop(i)
                                st.rerun()
                
                # Combine results from both methods
                all_dates = list(set(dates_from_text + dates_from_picker))  # Remove duplicates
                all_dates.sort()  # Sort chronologically
                
                if all_dates:
                    st.info(f"📅 Total: {len(all_dates)} unique dates selected" 
                        if self.lang == 'en' else 
                        f"📅 I alt: {len(all_dates)} unikke datoer valgt")
                
                return all_dates
            
            return []
    def _handle_individual_date_selection(self, param: str, constraint_name: str) -> List[str]:
        """Handle single date selection."""
        selected_date = st.date_input(
            f"Vælg {param}:" if self.lang == 'da' else f"Select {param}:",
            key=f"single_date_{constraint_name}_{param}",
            help="Vælg en enkelt dato" if self.lang == 'da' else "Select a single date"
        )
        
        if selected_date:
            return [selected_date.strftime('%Y-%m-%d')]
        else:
            return []

    def _handle_date_range_selection(self, param: str, constraint_name: str) -> List[str]:
        """Handle date range selection."""
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Start dato:" if self.lang == 'da' else "Start date:",
                key=f"start_date_{constraint_name}_{param}",
                help="Vælg startdato for interval" if self.lang == 'da' else "Select start date for range"
            )
        
        with col2:
            end_date = st.date_input(
                "Slut dato:" if self.lang == 'da' else "End date:",
                key=f"end_date_{constraint_name}_{param}",
                help="Vælg slutdato for interval" if self.lang == 'da' else "Select end date for range"
            )
        
        if start_date and end_date:
            if end_date >= start_date:
                # Generate date range
                dates = []
                current = start_date
                while current <= end_date:
                    dates.append(current.strftime('%Y-%m-%d'))
                    current += timedelta(days=1)
                
                # Show summary
                st.success(f"📅 {len(dates)} dage valgt: {dates[0]} til {dates[-1]}" if self.lang == 'da'
                        else f"📅 {len(dates)} days selected: {dates[0]} to {dates[-1]}")
                return dates
            else:
                st.error("Slut dato skal være efter start dato" if self.lang == 'da' 
                        else "End date must be after start date")
                return []
        else:
            if start_date or end_date:
                st.info("Vælg både start- og slutdato" if self.lang == 'da' 
                    else "Please select both start and end dates")
            return []

    def _handle_multiple_individual_dates(self, param: str, constraint_name: str) -> List[str]:
        """
        Handle multiple individual (non-consecutive) dates selection.
        FIXED: Improved session state management and UI feedback.
        """
        # Session state key for storing multiple dates
        dates_key = f"multi_dates_{constraint_name}_{param}"
        
        # Initialize session state
        if dates_key not in st.session_state:
            st.session_state[dates_key] = [None]  # Start with one empty date input
        
        st.write("📅 " + ("Vælg flere individuelle datoer:" if self.lang == 'da' 
                        else "Select multiple individual dates:"))
        
        dates_list = st.session_state[dates_key]
        selected_dates = []
        
        # FIXED: Better error handling and validation
        try:
            # Create columns for better layout
            for i, date_value in enumerate(dates_list):
                col1, col2, col3 = st.columns([6, 1, 1])
                
                with col1:
                    selected_date = st.date_input(
                        f"Dato {i+1}:" if self.lang == 'da' else f"Date {i+1}:",
                        value=date_value,
                        key=f"multi_date_{constraint_name}_{param}_{i}",
                        help=f"Vælg dato #{i+1}" if self.lang == 'da' else f"Select date #{i+1}"
                    )
                    
                    # Update session state
                    if selected_date != st.session_state[dates_key][i]:
                        st.session_state[dates_key][i] = selected_date
                    
                    if selected_date:
                        date_str = selected_date.strftime('%Y-%m-%d')
                        if date_str not in selected_dates:  # Avoid duplicates
                            selected_dates.append(date_str)
                
                with col2:
                    # Add button (only show on last row)
                    if i == len(dates_list) - 1:
                        if st.button("➕", key=f"add_date_{constraint_name}_{param}_{i}", 
                                help="Tilføj flere datoer" if self.lang == 'da' else "Add more dates"):
                            st.session_state[dates_key].append(None)
                            st.rerun()
                
                with col3:
                    # Remove button (only show if more than one date input)
                    if len(dates_list) > 1:
                        if st.button("❌", key=f"remove_date_{constraint_name}_{param}_{i}",
                                help="Fjern denne dato" if self.lang == 'da' else "Remove this date"):
                            st.session_state[dates_key].pop(i)
                            st.rerun()
            
            # Show summary of selected dates
            if selected_dates:
                st.success(f"✅ {len(selected_dates)} datoer valgt: {', '.join(selected_dates)}" if self.lang == 'da'
                        else f"✅ {len(selected_dates)} dates selected: {', '.join(selected_dates)}")
            
            # Alternative text input method
            st.write("---")
            st.write("**" + ("Eller indtast datoer som tekst:" if self.lang == 'da' 
                            else "Or enter dates as text:") + "**")
            
            text_dates = st.text_input(
                "Komma-separerede datoer (YYYY-MM-DD):" if self.lang == 'da' 
                else "Comma-separated dates (YYYY-MM-DD):",
                key=f"text_dates_{constraint_name}_{param}",
                placeholder="2025-07-15, 2025-07-20, 2025-07-25",
                help="Format: YYYY-MM-DD, YYYY-MM-DD, ..."
            )
            
            if text_dates.strip():
                try:
                    # Parse text input dates
                    text_date_list = []
                    for date_str in text_dates.split(','):
                        date_str = date_str.strip()
                        if date_str:
                            # Validate date format
                            datetime.strptime(date_str, '%Y-%m-%d')
                            text_date_list.append(date_str)
                    
                    if text_date_list:
                        st.info(f"📝 {len(text_date_list)} datoer fra tekst: {', '.join(text_date_list)}" if self.lang == 'da'
                            else f"📝 {len(text_date_list)} dates from text: {', '.join(text_date_list)}")
                        # Combine with GUI selected dates (remove duplicates)
                        all_dates = list(set(selected_dates + text_date_list))
                        return sorted(all_dates)
                
                except ValueError as e:
                    st.error(f"Ugyldig dato format. Brug YYYY-MM-DD format." if self.lang == 'da'
                            else f"Invalid date format. Use YYYY-MM-DD format.")
                    return selected_dates
            
            return selected_dates
            
        except Exception as e:
            st.error(f"Fejl i datovælger: {str(e)}" if self.lang == 'da' 
                    else f"Error in date selector: {str(e)}")
            return []

    def _clear_date_session_state(self, constraint_name: str, param: str):
        """Helper method to clear session state for date parameters."""
        keys_to_clear = [
            f"date_method_{constraint_name}_{param}",
            f"multi_dates_{constraint_name}_{param}",
            f"single_date_{constraint_name}_{param}",
            f"start_date_{constraint_name}_{param}",
            f"end_date_{constraint_name}_{param}",
            f"text_dates_{constraint_name}_{param}"
        ]
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]

    def _create_multiple_individual_dates(self, param: str, constraint_name: str) -> List[str]:
        """
        Create interface for selecting multiple individual (non-consecutive) dates.
        
        This uses a dynamic list of date inputs that users can add/remove.
        """
        # Session state key for storing multiple dates
        dates_key = f"multi_dates_{constraint_name}_{param}"
        
        # Initialize session state
        if dates_key not in st.session_state:
            st.session_state[dates_key] = [None]  # Start with one empty date input
        
        st.write("📅 " + ("Vælg flere individuelle datoer:" if self.lang == 'da' 
                         else "Select multiple individual dates:"))
        
        dates_list = st.session_state[dates_key]
        selected_dates = []
        
        # Create columns for better layout
        for i, date_value in enumerate(dates_list):
            col1, col2, col3 = st.columns([6, 1, 1])
            
            with col1:
                selected_date = st.date_input(
                    f"Dato {i+1}:" if self.lang == 'da' else f"Date {i+1}:",
                    value=date_value,
                    key=f"multi_date_{constraint_name}_{param}_{i}"
                )
                
                # Update session state
                if selected_date != st.session_state[dates_key][i]:
                    st.session_state[dates_key][i] = selected_date
                
                if selected_date:
                    selected_dates.append(selected_date.strftime('%Y-%m-%d'))
            
            with col2:
                # Add button (only show on last row)
                if i == len(dates_list) - 1:
                    if st.button("➕", key=f"add_date_{constraint_name}_{param}_{i}", 
                               help="Tilføj flere datoer" if self.lang == 'da' else "Add more dates"):
                        st.session_state[dates_key].append(None)
                        st.rerun()
            
            with col3:
                # Remove button (only show if more than one date input)
                if len(dates_list) > 1:
                    if st.button("❌", key=f"remove_date_{constraint_name}_{param}_{i}",
                               help="Fjern denne dato" if self.lang == 'da' else "Remove this date"):
                        st.session_state[dates_key].pop(i)
                        st.rerun()
        
        # Alternative text input method
        st.write("**" + ("Eller indtast datoer som tekst:" if self.lang == 'da' 
                        else "Or enter dates as text:") + "**")
        
        text_dates = st.text_input(
            "Datoer (YYYY-MM-DD, komma-separeret):" if self.lang == 'da' 
            else "Dates (YYYY-MM-DD, comma-separated):",
            placeholder="2025-07-15, 2025-07-18, 2025-07-22",
            key=f"text_dates_{constraint_name}_{param}",
            help="Eksempel: 2025-07-15, 2025-07-18, 2025-07-22" if self.lang == 'da'
                 else "Example: 2025-07-15, 2025-07-18, 2025-07-22"
        )
        
        # Parse text input dates
        text_parsed_dates = []
        if text_dates.strip():
            try:
                for date_str in text_dates.split(','):
                    date_str = date_str.strip()
                    if date_str:
                        # Validate date format
                        parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                        text_parsed_dates.append(date_str)
                
                if text_parsed_dates:
                    st.success(f"✅ {len(text_parsed_dates)} datoer parset fra tekst" if self.lang == 'da'
                             else f"✅ {len(text_parsed_dates)} dates parsed from text")
            except ValueError as e:
                st.error("Ugyldig dato format. Brug YYYY-MM-DD format." if self.lang == 'da'
                        else "Invalid date format. Use YYYY-MM-DD format.")
        
        # Combine dates from both methods
        all_dates = list(set(selected_dates + text_parsed_dates))  # Remove duplicates
        all_dates.sort()  # Sort chronologically
        
        # Show summary
        if all_dates:
            st.info(f"📅 **{len(all_dates)} datoer valgt i alt:**" if self.lang == 'da' 
                   else f"📅 **{len(all_dates)} dates selected total:**")
            
            # Show dates in a nice format
            if len(all_dates) <= 10:
                st.write(", ".join(all_dates))
            else:
                st.write(f"{', '.join(all_dates[:5])}, ... og {len(all_dates)-5} flere" if self.lang == 'da'
                        else f"{', '.join(all_dates[:5])}, ... and {len(all_dates)-5} more")
        
        return all_dates
    
    def validate_parameters(self, parameters: Dict[str, Any], required_params: List[str]) -> Tuple[bool, List[str]]:
        """Validate all parameters according to rules."""
        errors = []
        
        for param in required_params:
            value = parameters.get(param)
            
            # Check if required parameter is missing
            if value is None or (isinstance(value, str) and value.strip() == "") or \
               (isinstance(value, list) and len(value) == 0):
                errors.append(f"Parameter '{param}' is required")
                continue
            
            # Apply validation rule if exists
            rule = self.config.VALIDATION_RULES.get(param)
            if rule and not rule(value):
                message = self.config.VALIDATION_MESSAGES.get(param, f"Invalid value for {param}")
                errors.append(message)
        
        return len(errors) == 0, errors

    def _render_no_parameters_form(self, constraint_name: str, is_hard: bool) -> None:
        """Render form for constraints that don't need parameters."""
        st.info(
            "Denne begrænsning kræver ingen parametre" if self.lang == 'da'
            else "This constraint requires no parameters"
        )
        
        st.write(
            "Klik 'Tilføj' for at aktivere denne begrænsning." if self.lang == 'da'
            else "Click 'Add' to enable this constraint."
        )
        
        if st.button(
            "Tilføj Begrænsning" if self.lang == 'da' else "Add Constraint",
            type="primary",
            key=f"no_params_{constraint_name}"
        ):
            # Access data_manager
            data_manager = ConstraintDataManager(self.lang)
            if data_manager.save_constraint({}, constraint_name, is_hard):
                st.success(f"Constraint added: {constraint_name}")
    
    def _show_combination_preview(self, parameters: Dict[str, Any]) -> None:
        """Show preview of parameter combinations for multi-value parameters."""
        multi_params = {k: v for k, v in parameters.items() 
                       if isinstance(v, list) and len(v) > 1}
        
        if multi_params:
            total_combinations = 1
            for values in multi_params.values():
                total_combinations *= len(values)
            
            st.info(f"**Multiple values detected**")
            for param, values in multi_params.items():
                if len(values) <= 5:
                    st.write(f"- **{param}:** {', '.join(map(str, values))}")
                else:
                    st.write(f"- **{param}:** {len(values)} values")
            st.write(f"**Total combinations:** {total_combinations}")
    
    def _process_form_submission(self, parameters: Dict[str, Any], required_params: List[str], 
                                constraint_name: str, is_hard: bool) -> None:
        """Process form submission with validation and constraint generation."""
        # Validate parameters
        is_valid, errors = self.validate_parameters(parameters, required_params)
        
        if not is_valid:
            st.error("Validation errors:" if self.lang == 'en' else "Validerings fejl:")
            for error in errors:
                st.error(f"• {error}")
            return
        
        # Generate constraint combinations
        constraints_to_add = self._generate_constraint_combinations(parameters)
        
        # Access data_manager
        data_manager = ConstraintDataManager(self.lang)
        
        # Save constraints
        if len(constraints_to_add) == 1:
            success = data_manager.save_constraint(constraints_to_add[0], constraint_name, is_hard)
        else:
            success = data_manager.save_multiple_constraints(constraints_to_add, constraint_name, is_hard)
        
        if success:
            st.success(f"Added {len(constraints_to_add)} constraint(s)")
            
            # Show summary
            with st.expander("Added constraints" if self.lang == 'en' else "Tilføjede begrænsninger"):
                for i, constraint in enumerate(constraints_to_add[:5]):  # Show first 5
                    st.write(f"**{i+1}:** {constraint}")
                if len(constraints_to_add) > 5:
                    st.write(f"... and {len(constraints_to_add) - 5} more")
    
    def _generate_constraint_combinations(self, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate all constraint combinations from multi-value parameters."""
        import itertools
        
        # Separate single and multi-value parameters
        single_params = {}
        multi_params = {}
        
        for param, value in parameters.items():
            if value is None or value == "" or (isinstance(value, list) and len(value) == 0):
                continue
            elif isinstance(value, list) and len(value) > 1:
                multi_params[param] = value
            elif isinstance(value, list) and len(value) == 1:
                single_params[param] = value[0]
            else:
                single_params[param] = value
        
        # Generate combinations
        if not multi_params:
            return [single_params] if single_params else [{}]
        
        # Use itertools.product for Cartesian product
        param_names = list(multi_params.keys())
        param_values = list(multi_params.values())
        combinations = list(itertools.product(*param_values))
        
        # Create constraint list
        constraints = []
        for combination in combinations:
            constraint_params = single_params.copy()
            for i, param_name in enumerate(param_names):
                constraint_params[param_name] = combination[i]
            constraints.append(constraint_params)
        
        return constraints

class ConstraintDataManager:
    """Handles all constraint data operations - loading, saving, editing."""
    
    def __init__(self, lang: str = 'da'):
        self.lang = lang
    
    def load_available_constraints(self) -> Dict[str, Dict]:
        """Load available constraints from constraint loader classes."""
        try:
            from core.hard_constraints import HardConstraintLoader
            from core.soft_constraints import SoftConstraintLoader
            
            hard_loader = HardConstraintLoader("dummy_path")
            soft_loader = SoftConstraintLoader("dummy_path")
            
            return {
                'hard': hard_loader.constraint_types,
                'soft': soft_loader.constraint_types
            }
        except Exception as e:
            st.error(f"Error loading constraint types: {e}")
            return {'hard': {}, 'soft': {}}
    
    def save_constraint(self, parameters: Dict[str, Any], constraint_name: str, is_hard: bool) -> bool:
        """Save a single constraint and update session state."""
        converted_params = self._convert_parameters_to_strings(parameters)
        converted_params['constraint_type'] = constraint_name
        
        # Get file path
        file_paths = get_file_paths()
        constraint_file = file_paths['hard_constraints'] if is_hard else file_paths['soft_constraints']
        
        # Load existing constraints
        existing_df = load_constraints(constraint_file)
        
        # Add new constraint
        new_constraint_df = pd.DataFrame([converted_params])
        updated_df = pd.concat([existing_df, new_constraint_df], ignore_index=True)
        
        # Save to file
        success = save_dataframe(updated_df, constraint_file, "Constraint added successfully")
        
        # NEW: Update session state to refresh the display automatically
        if success:
            constraint_type = 'hard' if is_hard else 'soft'
            session_key = f"{constraint_type}_constraints_df"
            st.session_state[session_key] = updated_df
        
        return success
    
    def save_multiple_constraints(self, constraints_list: List[Dict[str, Any]], 
                                constraint_name: str, is_hard: bool) -> bool:
        """Save multiple constraints and update session state."""
        if not constraints_list:
            return False
        
        # Convert all constraints
        converted_constraints = []
        for constraint_params in constraints_list:
            converted_params = self._convert_parameters_to_strings(constraint_params)
            converted_params['constraint_type'] = constraint_name
            converted_constraints.append(converted_params)
        
        # Get file path
        file_paths = get_file_paths()
        constraint_file = file_paths['hard_constraints'] if is_hard else file_paths['soft_constraints']
        
        # Load existing constraints
        existing_df = load_constraints(constraint_file)
        
        # Add new constraints
        new_constraints_df = pd.DataFrame(converted_constraints)
        updated_df = pd.concat([existing_df, new_constraints_df], ignore_index=True)
        
        # Save to file
        success = save_dataframe(updated_df, constraint_file, 
                            f"{len(constraints_list)} constraints added successfully")
        
        # NEW: Update session state to refresh the display automatically
        if success:
            constraint_type = 'hard' if is_hard else 'soft'
            session_key = f"{constraint_type}_constraints_df"
            st.session_state[session_key] = updated_df
        
        return success
    
    def render_existing_constraints(self) -> None:
        """Render the existing constraints display and editing interface."""
        st.subheader("Existing Constraints" if self.lang == 'en' else "Eksisterende Begrænsninger")
        
        file_paths = get_file_paths()
        
        # Create tabs for hard and soft constraints
        tab1, tab2 = st.tabs([
            "Hard Constraints" if self.lang == 'en' else "Hårde Begrænsninger",
            "Soft Constraints" if self.lang == 'en' else "Bløde Begrænsninger"
        ])
        
        with tab1:
            self._render_constraint_editor(file_paths['hard_constraints'], 'hard')
        
        with tab2:
            self._render_constraint_editor(file_paths['soft_constraints'], 'soft')
    
    def _render_constraint_editor(self, constraint_file: str, constraint_type: str) -> None:
        """Render editable constraints table for a specific type."""
        # Initialize session state
        session_key = f"{constraint_type}_constraints_df"
        if session_key not in st.session_state:
            st.session_state[session_key] = load_constraints(constraint_file)
        
        constraints_df = st.session_state[session_key]
        
        if not constraints_df.empty:
            # Action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button(f"Save {constraint_type.title()}", key=f"save_{constraint_type}"):
                    if save_dataframe(st.session_state[session_key], constraint_file, 
                                    "Data saved successfully"):
                        st.success(f"{constraint_type.title()} constraints saved!")
            
            with col2:
                if st.button(f"Refresh {constraint_type.title()}", key=f"refresh_{constraint_type}"):
                    st.session_state[session_key] = load_constraints(constraint_file)
                    st.success("Data refreshed!")
                    st.rerun()
            
            with col3:
                if st.button(f"Clear All {constraint_type.title()}", key=f"clear_{constraint_type}"):
                    if st.button(f"Confirm Clear {constraint_type.title()}", key=f"confirm_clear_{constraint_type}"):
                        st.session_state[session_key] = pd.DataFrame(columns=['constraint_type'])
                        st.success("Cleared! Don't forget to save.")
                        st.rerun()
            
            # Editable dataframe
            edited_df = st.data_editor(
                constraints_df,
                num_rows="dynamic",
                width='stretch',
                key=f"editor_{constraint_type}"
            )
            
            # Update session state if edited
            if not edited_df.equals(constraints_df):
                st.session_state[session_key] = edited_df
        
        else:
            st.info("No constraints defined" if self.lang == 'en' else "Ingen begrænsninger defineret")
            if st.button(f"Create Empty {constraint_type.title()} File", key=f"create_{constraint_type}"):
                empty_df = pd.DataFrame(columns=['constraint_type'])
                if save_dataframe(empty_df, constraint_file, f"Empty {constraint_type} file created"):
                    st.session_state[session_key] = empty_df
                    st.rerun()
    
    def _convert_parameters_to_strings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Convert parameter objects to strings for storage."""
        converted = {}
        for param, value in params.items():
            if hasattr(value, 'strftime'):
                if hasattr(value, 'hour'):  # Time object
                    converted[param] = value.strftime('%H:%M')
                else:  # Date object
                    converted[param] = value.strftime('%Y-%m-%d')
            elif isinstance(value, list):
                converted[param] = ','.join(map(str, value))
            else:
                converted[param] = value
        return converted

class ConstraintFormManager:
    """Main manager for constraint form interface - coordinates all constraint operations."""
    
    def __init__(self, lang: str = 'da'):
        self.lang = lang
        self.parameter_handler = ConstraintParameterHandler(lang)
        self.data_manager = ConstraintDataManager(lang)
    
    def render_constraint_form(self, constraint_name: str, required_params: Union[List, Dict], 
                                   employees_df: pd.DataFrame, is_hard: bool) -> None:
        """
        ALTERNATIVE: No forms approach - all parameters are interactive immediately.
        
        This might be even better for user experience since everything updates in real-time.
        """
        st.subheader("Constraint Parameters" if self.lang == 'en' else "Begrænsningsparametre")
        #st.write(f"**{constraint_name.replace('_', ' ').title()}**")
        
        # Handle method selection for flexible parameters
        method_params = required_params
        if isinstance(required_params, dict):
            method_params = self.parameter_handler._handle_flexible_parameters(required_params, constraint_name)
        elif required_params is None:
            method_params = []
        else:
            method_params = list(required_params)
        
        # Auto-add weight for soft constraints
        if not is_hard and 'weight' not in method_params:
            method_params.append('weight')
        
        # Handle constraints with no parameters
        if not method_params:
            st.info(
                "Denne begrænsning kræver ingen parametre" if self.lang == 'da'
                else "This constraint requires no parameters"
            )
            if st.button(
                "Add Constraint" if self.lang == 'en' else "Tilføj Begrænsning",
                type="primary",
                key=f"submit_no_params_{constraint_name}"
            ):
                self._process_form_submission({}, [], constraint_name, is_hard)
            return
        
        # Render ALL parameters outside of forms
        all_parameters = self.parameter_handler.render_parameters(method_params, constraint_name, employees_df)
        
        # Show combination preview
        self._show_combination_preview(all_parameters)
        
        # Submit button (no form needed)
        if st.button(
            "Add Constraint" if self.lang == 'en' else "Tilføj Begrænsning",
            type="primary",
            key=f"submit_{constraint_name}"
        ):
            self._process_form_submission(all_parameters, method_params, constraint_name, is_hard)

    def _render_no_parameters_form(self, constraint_name: str, is_hard: bool) -> None:
        """Render form for constraints that don't need parameters."""
        st.info(
            "Denne begrænsning kræver ingen parametre" if self.lang == 'da'
            else "This constraint requires no parameters"
        )
        
        with st.form(f"no_params_form_{constraint_name}"):
            st.write(
                "Klik 'Tilføj' for at aktivere denne begrænsning." if self.lang == 'da'
                else "Click 'Add' to enable this constraint."
            )
            
            submitted = st.form_submit_button(
                "Add Constraint" if self.lang == 'en' else "Tilføj Begrænsning",
                type="primary"
            )
            
            if submitted:
                if self.data_manager.save_constraint({}, constraint_name, is_hard):
                    st.success(f"Constraint added: {constraint_name}")
    
    def _show_combination_preview(self, parameters: Dict[str, Any]) -> None:
        """Show preview of parameter combinations for multi-value parameters."""
        multi_params = {k: v for k, v in parameters.items() 
                       if isinstance(v, list) and len(v) > 1}
        
        if multi_params:
            total_combinations = 1
            for values in multi_params.values():
                total_combinations *= len(values)
            
            st.info(f"**Multiple values detected**")
            for param, values in multi_params.items():
                if len(values) <= 5:
                    st.write(f"- **{param}:** {', '.join(map(str, values))}")
                else:
                    st.write(f"- **{param}:** {len(values)} values")
            st.write(f"**Total combinations:** {total_combinations}")
    
    def _process_form_submission(self, parameters: Dict[str, Any], required_params: List[str], 
                                constraint_name: str, is_hard: bool) -> None:
        """Process form submission with validation and constraint generation."""
        # Validate parameters
        is_valid, errors = self.parameter_handler.validate_parameters(parameters, required_params)
        
        if not is_valid:
            st.error("Validation errors:" if self.lang == 'en' else "Validerings fejl:")
            for error in errors:
                st.error(f"• {error}")
            return
        
        # Generate constraint combinations
        constraints_to_add = self._generate_constraint_combinations(parameters)
        
        # Save constraints
        if len(constraints_to_add) == 1:
            success = self.data_manager.save_constraint(constraints_to_add[0], constraint_name, is_hard)
        else:
            success = self.data_manager.save_multiple_constraints(constraints_to_add, constraint_name, is_hard)
        
        if success:
            st.success(f"Added {len(constraints_to_add)} constraint(s)")
            
            # Show summary
            with st.expander("Added constraints" if self.lang == 'en' else "Tilføjede begrænsninger"):
                for i, constraint in enumerate(constraints_to_add[:5]):  # Show first 5
                    st.write(f"**{i+1}:** {constraint}")
                if len(constraints_to_add) > 5:
                    st.write(f"... and {len(constraints_to_add) - 5} more")
    
    def _generate_constraint_combinations(self, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate all constraint combinations from multi-value parameters."""
        # Separate single and multi-value parameters
        single_params = {}
        multi_params = {}
        
        for param, value in parameters.items():
            if value is None or value == "" or (isinstance(value, list) and len(value) == 0):
                continue
            elif isinstance(value, list) and len(value) > 1:
                multi_params[param] = value
            elif isinstance(value, list) and len(value) == 1:
                single_params[param] = value[0]
            else:
                single_params[param] = value
        
        # Generate combinations
        if not multi_params:
            return [single_params] if single_params else [{}]
        
        # Use itertools.product for Cartesian product
        param_names = list(multi_params.keys())
        param_values = list(multi_params.values())
        combinations = list(itertools.product(*param_values))
        
        # Create constraint list
        constraints = []
        for combination in combinations:
            constraint_params = single_params.copy()
            for i, param_name in enumerate(param_names):
                constraint_params[param_name] = combination[i]
            constraints.append(constraint_params)
        
        return constraints

    def clear_constraint_session_state(self, constraint_name: str):
        """Clear session state for constraint-specific data when switching constraints."""
        keys_to_clear = [key for key in st.session_state.keys() 
                        if key.startswith(f"dates_{constraint_name}")]
        
        for key in keys_to_clear:
            del st.session_state[key]

    def clear_constraint_session_state_on_change(self):
        """Clear constraint-specific session state when switching constraints."""
        # Get all constraint-related session state keys
        keys_to_clear = []
        for key in st.session_state.keys():
            if key.startswith('dates_') or key.startswith('new_date_') or key.startswith('date_method_'):
                keys_to_clear.append(key)
        
        # Clear them
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]

# =============================================================================
# SIMPLIFIED CONSTRAINT TAB INTERFACE
# =============================================================================

def show_constraints_tab(lang):
    """
    Simplified main constraints tab interface.
    """
    st.header("Constraints" if lang == 'en' else "Begrænsninger")
    
    # Initialize managers
    form_manager = ConstraintFormManager(lang)
    data_manager = ConstraintDataManager(lang)
    
    # Load available constraints and employees
    available_constraints = data_manager.load_available_constraints()
    file_paths = get_file_paths()
    employees_df = load_employees(file_paths['employees'])
    
    # Ensure employees_df has proper structure
    if employees_df.empty or 'ID' not in employees_df.columns:
        employees_df = create_empty_employees_df()
    
    # Constraint category selection
    constraint_category = st.radio(
        "Constraint Type:" if lang == 'en' else "Begrænsningstype:",
        [get_text("hard_constraints",lang),
         get_text("soft_constraints",lang)]
    )
    
    is_hard = (get_text("hard_constraints",lang) == constraint_category)
    constraint_types = available_constraints['hard'] if is_hard else available_constraints['soft']
    
    # Filter constraints for UI
    filtered_constraints = {name: (class_obj, required_params) 
                          for name, (class_obj, required_params) in constraint_types.items()}
    
    # Constraint selection
    if filtered_constraints:
        constraint_names = list(filtered_constraints.keys())
        selected_constraint = st.selectbox(
            "Select Constraint:" if lang == 'en' else "Vælg Begrænsning:",
            [""] + constraint_names,
            format_func=lambda x: x.replace('_', ' ').title() if x else ""
        )
        
        # Show constraint form when selected
        if selected_constraint:
            required_params = filtered_constraints[selected_constraint][1]
            form_manager.render_constraint_form(
                selected_constraint, required_params, employees_df, is_hard
            )
    else:
        st.info("No constraints available" if lang == 'en' else "Ingen begrænsninger tilgængelige")
    
    # Show existing constraints
    data_manager.render_existing_constraints()

def merge_constraint_files(primary_file_path, additional_file_path, constraint_type):
    """
    Merge two constraint files of the same type, handling different columns and orders.
    
    Args:
        primary_file_path: Path to the primary constraints file
        additional_file_path: Path to the additional constraints file
        constraint_type: 'hard' or 'soft' for error messaging
        
    Returns:
        pandas.DataFrame: Merged constraints dataframe
    """
    import pandas as pd
    import os
    
    # Load primary file
    try:
        if os.path.exists(primary_file_path):
            primary_df = load_constraints(primary_file_path)
        else:
            primary_df = pd.DataFrame(columns=['constraint_type'])
    except Exception as e:
        st.warning(f"Could not load primary {constraint_type} constraints file: {e}")
        primary_df = pd.DataFrame(columns=['constraint_type'])
    
    # Load additional file
    try:
        if os.path.exists(additional_file_path):
            additional_df = load_constraints(additional_file_path)
        else:
            st.info(f"Additional {constraint_type} constraints file not found, using primary only")
            return primary_df
    except Exception as e:
        st.warning(f"Could not load additional {constraint_type} constraints file: {e}")
        return primary_df
    
    # Handle empty dataframes
    if primary_df.empty and additional_df.empty:
        return pd.DataFrame(columns=['constraint_type'])
    elif primary_df.empty:
        return additional_df
    elif additional_df.empty:
        return primary_df
    
    # Get all unique columns from both dataframes
    all_columns = list(set(primary_df.columns.tolist() + additional_df.columns.tolist()))
    
    # Ensure 'constraint_type' is first if it exists
    if 'constraint_type' in all_columns:
        all_columns.remove('constraint_type')
        all_columns.insert(0, 'constraint_type')
    
    # Add missing columns to both dataframes with appropriate default values
    for col in all_columns:
        if col not in primary_df.columns:
            primary_df[col] = pd.NA
        if col not in additional_df.columns:
            additional_df[col] = pd.NA
    
    # Reorder columns to match
    primary_df = primary_df.reindex(columns=all_columns)
    additional_df = additional_df.reindex(columns=all_columns)
    
    # Merge the dataframes
    merged_df = pd.concat([primary_df, additional_df], ignore_index=True)
    
    # Ensure proper data types
    merged_df = ensure_proper_constraint_data_types(merged_df)
    
    return merged_df

def show_constraint_file_merger_ui(lang):
    """
    Show UI controls for selecting and merging constraint files.
    
    Returns:
        dict: Dictionary with merged file paths
    """
    
    # Enable/disable constraint file merging
    use_constraint_merging = st.checkbox(
        "Kombiner flere begrænsningsfiler" if lang == 'da' else "Combine multiple constraint files",
        value=False,
        help="Aktivér for at kombinere en base begrænsningsfil med en specifik fil" if lang == 'da' 
             else "Enable to combine a base constraint file with a specific file"
    )
    
    merged_file_paths = {}
    
    if use_constraint_merging:
        st.info(
            "💡 **Tip:** Du kan have en 'base' fil med begrænsninger der gælder for alle vagtplaner, "
            "og en 'specifik' fil kun for denne vagtplan." if lang == 'da' else
            "💡 **Tip:** You can have a 'base' file with constraints that apply to all schedules, "
            "and a 'specific' file just for this schedule."
        )
        
        # Hard constraints merging
        with st.expander("⚙️ " + ("Hårde Begrænsninger" if lang == 'da' else "Hard Constraints"), expanded=True):
            st.write("**" + ("Kombiner hårde begrænsningsfiler:" if lang == 'da' else "Combine hard constraint files:") + "**")
            
            # Primary hard constraints file
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**" + ("Base fil (primær):" if lang == 'da' else "Base file (primary):") + "**")
                primary_hard_method = st.radio(
                    "Input metode:" if lang == 'da' else "Input method:",
                    ["Angiv sti" if lang == 'da' else "Specify path", 
                     "Upload fil" if lang == 'da' else "Upload file"],
                    horizontal=True,
                    key="primary_hard_method"
                )
                
                if primary_hard_method == ("Upload fil" if lang == 'da' else "Upload file"):
                    primary_hard_file = st.file_uploader(
                        "Upload base hårde begrænsninger" if lang == 'da' else "Upload base hard constraints",
                        type=['xlsx', 'xls'],
                        key="primary_hard_uploader"
                    )
                    
                    if primary_hard_file is not None:
                        import tempfile
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                            tmp_file.write(primary_hard_file.getvalue())
                            primary_hard_path = tmp_file.name
                        st.success("✅ " + ("Base fil uploadet" if lang == 'da' else "Base file uploaded"))
                    else:
                        primary_hard_path = get_file_paths()['hard_constraints']
                        st.info("🔄 " + ("Bruger standard sti" if lang == 'da' else "Using default path"))
                else:
                    primary_hard_path = st.text_input(
                        "Sti til base hårde begrænsninger:" if lang == 'da' else "Path to base hard constraints:",
                        value=get_file_paths()['hard_constraints'],
                        key="primary_hard_path"
                    )
            
            with col2:
                st.write("**" + ("Specifik fil (tillæg):" if lang == 'da' else "Specific file (additional):") + "**")
                additional_hard_method = st.radio(
                    "Input metode:" if lang == 'da' else "Input method:",
                    ["Angiv sti" if lang == 'da' else "Specify path", 
                     "Upload fil" if lang == 'da' else "Upload file"],
                    horizontal=True,
                    key="additional_hard_method"
                )
                
                if additional_hard_method == ("Upload fil" if lang == 'da' else "Upload file"):
                    additional_hard_file = st.file_uploader(
                        "Upload specifikke hårde begrænsninger" if lang == 'da' else "Upload specific hard constraints",
                        type=['xlsx', 'xls'],
                        key="additional_hard_uploader"
                    )
                    
                    if additional_hard_file is not None:
                        import tempfile
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                            tmp_file.write(additional_hard_file.getvalue())
                            additional_hard_path = tmp_file.name
                        st.success("✅ " + ("Specifik fil uploadet" if lang == 'da' else "Specific file uploaded"))
                    else:
                        additional_hard_path = ""
                        st.info("ℹ️ " + ("Ingen specifik fil valgt" if lang == 'da' else "No specific file selected"))
                else:
                    additional_hard_path = st.text_input(
                        "Sti til specifikke hårde begrænsninger:" if lang == 'da' else "Path to specific hard constraints:",
                        value="",
                        placeholder="./specific_hard_constraints.xlsx",
                        key="additional_hard_path"
                    )
            
            # Show merge preview for hard constraints
            if primary_hard_path and additional_hard_path:
                if st.button("🔍 " + ("Forhåndsvis sammenføjning (hård)" if lang == 'da' else "Preview merge (hard)"), 
                           key="preview_hard_merge"):
                    try:
                        merged_hard = merge_constraint_files(primary_hard_path, additional_hard_path, "hard")
                        if not merged_hard.empty:
                            st.write("**" + ("Sammenføjet resultat:" if lang == 'da' else "Merged result:") + "**")
                            st.dataframe(merged_hard, width='stretch')
                            st.info(f"📊 Total: {len(merged_hard)} hårde begrænsninger" if lang == 'da' 
                                   else f"📊 Total: {len(merged_hard)} hard constraints")
                        else:
                            st.warning("Ingen begrænsninger at vise" if lang == 'da' else "No constraints to show")
                    except Exception as e:
                        st.error(f"Fejl ved sammenføjning: {e}" if lang == 'da' else f"Error merging: {e}")
            
            # Store paths for hard constraints
            merged_file_paths['hard_primary'] = primary_hard_path if primary_hard_path else ""
            merged_file_paths['hard_additional'] = additional_hard_path if additional_hard_path else ""
        
        # Soft constraints merging
        with st.expander("🎯 " + ("Bløde Begrænsninger" if lang == 'da' else "Soft Constraints"), expanded=True):
            st.write("**" + ("Kombiner bløde begrænsningsfiler:" if lang == 'da' else "Combine soft constraint files:") + "**")
            
            # Primary soft constraints file
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**" + ("Base fil (primær):" if lang == 'da' else "Base file (primary):") + "**")
                primary_soft_method = st.radio(
                    "Input metode:" if lang == 'da' else "Input method:",
                    ["Angiv sti" if lang == 'da' else "Specify path", 
                     "Upload fil" if lang == 'da' else "Upload file"],
                    horizontal=True,
                    key="primary_soft_method"
                )
                
                if primary_soft_method == ("Upload fil" if lang == 'da' else "Upload file"):
                    primary_soft_file = st.file_uploader(
                        "Upload base bløde begrænsninger" if lang == 'da' else "Upload base soft constraints",
                        type=['xlsx', 'xls'],
                        key="primary_soft_uploader"
                    )
                    
                    if primary_soft_file is not None:
                        import tempfile
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                            tmp_file.write(primary_soft_file.getvalue())
                            primary_soft_path = tmp_file.name
                        st.success("✅ " + ("Base fil uploadet" if lang == 'da' else "Base file uploaded"))
                    else:
                        primary_soft_path = get_file_paths()['soft_constraints']
                        st.info("🔄 " + ("Bruger standard sti" if lang == 'da' else "Using default path"))
                else:
                    primary_soft_path = st.text_input(
                        "Sti til base bløde begrænsninger:" if lang == 'da' else "Path to base soft constraints:",
                        value=get_file_paths()['soft_constraints'],
                        key="primary_soft_path"
                    )
            
            with col2:
                st.write("**" + ("Specifik fil (tillæg):" if lang == 'da' else "Specific file (additional):") + "**")
                additional_soft_method = st.radio(
                    "Input metode:" if lang == 'da' else "Input method:",
                    ["Angiv sti" if lang == 'da' else "Specify path", 
                     "Upload fil" if lang == 'da' else "Upload file"],
                    horizontal=True,
                    key="additional_soft_method"
                )
                
                if additional_soft_method == ("Upload fil" if lang == 'da' else "Upload file"):
                    additional_soft_file = st.file_uploader(
                        "Upload specifikke bløde begrænsninger" if lang == 'da' else "Upload specific soft constraints",
                        type=['xlsx', 'xls'],
                        key="additional_soft_uploader"
                    )
                    
                    if additional_soft_file is not None:
                        import tempfile
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                            tmp_file.write(additional_soft_file.getvalue())
                            additional_soft_path = tmp_file.name
                        st.success("✅ " + ("Specifik fil uploadet" if lang == 'da' else "Specific file uploaded"))
                    else:
                        additional_soft_path = ""
                        st.info("ℹ️ " + ("Ingen specifik fil valgt" if lang == 'da' else "No specific file selected"))
                else:
                    additional_soft_path = st.text_input(
                        "Sti til specifikke bløde begrænsninger:" if lang == 'da' else "Path to specific soft constraints:",
                        value="",
                        placeholder="./specific_soft_constraints.xlsx",
                        key="additional_soft_path"
                    )
            
            # Show merge preview for soft constraints
            if primary_soft_path and additional_soft_path:
                if st.button("🔍 " + ("Forhåndsvis sammenføjning (blød)" if lang == 'da' else "Preview merge (soft)"), 
                           key="preview_soft_merge"):
                    try:
                        merged_soft = merge_constraint_files(primary_soft_path, additional_soft_path, "soft")
                        if not merged_soft.empty:
                            st.write("**" + ("Sammenføjet resultat:" if lang == 'da' else "Merged result:") + "**")
                            st.dataframe(merged_soft, width='stretch')
                            st.info(f"📊 Total: {len(merged_soft)} bløde begrænsninger" if lang == 'da' 
                                   else f"📊 Total: {len(merged_soft)} soft constraints")
                        else:
                            st.warning("Ingen begrænsninger at vise" if lang == 'da' else "No constraints to show")
                    except Exception as e:
                        st.error(f"Fejl ved sammenføjning: {e}" if lang == 'da' else f"Error merging: {e}")
            
            # Store paths for soft constraints
            merged_file_paths['soft_primary'] = primary_soft_path if primary_soft_path else ""
            merged_file_paths['soft_additional'] = additional_soft_path if additional_soft_path else ""
        
        # Show summary of what will be merged
        st.write("**" + ("Sammenføjnings oversigt:" if lang == 'da' else "Merge summary:") + "**")
        
        # Hard constraints summary
        hard_summary = []
        if merged_file_paths.get('hard_primary'):
            hard_summary.append(f"Base: {merged_file_paths['hard_primary']}")
        if merged_file_paths.get('hard_additional'):
            hard_summary.append(f"Tillæg: {merged_file_paths['hard_additional']}" if lang == 'da' else f"Additional: {merged_file_paths['hard_additional']}")
        
        if hard_summary:
            st.write("🔗 **" + ("Hårde begrænsninger:" if lang == 'da' else "Hard constraints:") + "**")
            for item in hard_summary:
                st.write(f"  • {item}")
        
        # Soft constraints summary
        soft_summary = []
        if merged_file_paths.get('soft_primary'):
            soft_summary.append(f"Base: {merged_file_paths['soft_primary']}")
        if merged_file_paths.get('soft_additional'):
            soft_summary.append(f"Tillæg: {merged_file_paths['soft_additional']}" if lang == 'da' else f"Additional: {merged_file_paths['soft_additional']}")
        
        if soft_summary:
            st.write("🔗 **" + ("Bløde begrænsninger:" if lang == 'da' else "Soft constraints:") + "**")
            for item in soft_summary:
                st.write(f"  • {item}")
    
    return merged_file_paths if use_constraint_merging else {}

def create_merged_constraint_files(merged_file_paths, lang):
    """
    Create temporary merged constraint files and return their paths.
    
    Args:
        merged_file_paths: Dictionary with primary and additional file paths
        lang: Language code
        
    Returns:
        dict: Dictionary with paths to merged constraint files
    """
    import tempfile
    import os
    
    result_paths = {}
    
    # Handle hard constraints merging
    if merged_file_paths.get('hard_primary') or merged_file_paths.get('hard_additional'):
        primary_hard = merged_file_paths.get('hard_primary', "")
        additional_hard = merged_file_paths.get('hard_additional', "")
        
        if primary_hard and additional_hard:
            # Both files specified - merge them
            merged_hard = merge_constraint_files(primary_hard, additional_hard, "hard")
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='_merged_hard.xlsx') as tmp_file:
                merged_hard.to_excel(tmp_file.name, index=False)
                result_paths['hard_constraints'] = tmp_file.name
            
            st.success(f"✅ " + (f"Sammenføjede {len(merged_hard)} hårde begrænsninger" if lang == 'da' 
                               else f"Merged {len(merged_hard)} hard constraints"))
        
        elif primary_hard:
            # Only primary file specified
            result_paths['hard_constraints'] = primary_hard
            st.info("ℹ️ " + ("Bruger kun base hårde begrænsninger" if lang == 'da' 
                           else "Using only base hard constraints"))
        
        elif additional_hard:
            # Only additional file specified
            result_paths['hard_constraints'] = additional_hard
            st.info("ℹ️ " + ("Bruger kun specifikke hårde begrænsninger" if lang == 'da' 
                           else "Using only specific hard constraints"))
    
    # Handle soft constraints merging
    if merged_file_paths.get('soft_primary') or merged_file_paths.get('soft_additional'):
        primary_soft = merged_file_paths.get('soft_primary', "")
        additional_soft = merged_file_paths.get('soft_additional', "")
        
        if primary_soft and additional_soft:
            # Both files specified - merge them
            merged_soft = merge_constraint_files(primary_soft, additional_soft, "soft")
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='_merged_soft.xlsx') as tmp_file:
                merged_soft.to_excel(tmp_file.name, index=False)
                result_paths['soft_constraints'] = tmp_file.name
            
            st.success(f"✅ " + (f"Sammenføjede {len(merged_soft)} bløde begrænsninger" if lang == 'da' 
                               else f"Merged {len(merged_soft)} soft constraints"))
        
        elif primary_soft:
            # Only primary file specified
            result_paths['soft_constraints'] = primary_soft
            st.info("ℹ️ " + ("Bruger kun base bløde begrænsninger" if lang == 'da' 
                           else "Using only base soft constraints"))
        
        elif additional_soft:
            # Only additional file specified
            result_paths['soft_constraints'] = additional_soft
            st.info("ℹ️ " + ("Bruger kun specifikke bløde begrænsninger" if lang == 'da' 
                           else "Using only specific soft constraints"))
    
    return result_paths

# =============================================================================
# ENHANCED MODEL RUNNING TAB WITH HISTORICAL SCHEDULE SUPPORT
# =============================================================================

def load_holidays_from_json(filename="holidays.json"):
    """Load holidays from JSON file, return empty list if file doesn't exist"""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            # Convert string dates back to date objects
            return [datetime.strptime(date_str, '%Y-%m-%d').date() for date_str in data]
    except FileNotFoundError:
        return []  # Return empty list if file doesn't exist
    except json.JSONDecodeError:
        st.error(f"Error reading {filename}. Starting with empty holiday list.")
        return []
    except Exception as e:
        st.error(f"Unexpected error loading holidays: {e}")
        return []

def save_holidays_to_json(holiday_list, filename="holidays.json"):
    """Save holidays to JSON file"""
    try:
        # Convert date objects to strings for JSON storage
        date_strings = [holiday.strftime('%Y-%m-%d') for holiday in holiday_list]
        with open(filename, 'w') as f:
            json.dump(date_strings, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving holidays to {filename}: {e}")
        return False

def run_constraint_testing_simple(test_start_date, test_end_date, max_test_time, historical_file_path, lang, test_hard_constraints=None):
    """Simple constraint testing using your elegant approach."""
    
    # Get file paths
    file_paths = get_file_paths()
    
    # Use provided test_hard_constraints if available, otherwise fall back to default
    hard_constraints_file = test_hard_constraints if test_hard_constraints else file_paths['hard_constraints']
    
    # Show a spinner while running
    with st.spinner("Tester begrænsninger..." if lang == 'da' else "Testing constraints..."):
        
        # Capture output in a container for real-time updates
        output_container = st.container()
        
        # Redirect print statements to capture them
        import io
        import sys
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        
        try:
            with redirect_stdout(f):
                # Import your elegant function (assuming it's in constraint_testing.py)
                from core.main import run_constraints_test
                
                result = run_constraints_test(
                    test_start_date,
                    test_end_date,
                    file_paths['employees'],
                    file_paths['shifts'],
                    hard_constraints_file,  # Use the selected hard constraints file
                    historical_file_path
                )
            
            # Show the captured output
            output = f.getvalue()
            if output:
                with output_container:
                    st.subheader("🔍 " + ("Test Resultater:" if lang == 'da' else "Test Results:"))
                    
                    # Parse and display results nicely
                    lines = output.split('\n')
                    for line in lines:
                        if '❌' in line:
                            st.error(line)
                        elif '✅' in line:
                            st.success(line)
                        elif line.strip() and not line.startswith('Loaded'):
                            st.info(line)
            
            if result:
                st.success("🎉 " + ("Test fuldført succesfuldt!" if lang == 'da' else "Testing completed successfully!"))
                
                # Show which constraints file was used
                if test_hard_constraints:
                    st.info("ℹ️ " + ("Brugte sammenføjede begrænsninger" if lang == 'da' else "Used merged constraints"))
                else:
                    st.info("ℹ️ " + ("Brugte standard begrænsninger" if lang == 'da' else "Used default constraints"))
            else:
                st.error("❌ " + ("Test fejlede!" if lang == 'da' else "Testing failed!"))
                
        except Exception as e:
            st.error(f"Fejl under test: {e}" if lang == 'da' else f"Error during testing: {e}")
            
            # Show traceback for debugging
            import traceback
            with st.expander("Debug Information"):
                st.text(traceback.format_exc())

def show_run_model_tab(lang):
    """Display the enhanced model running interface with constraint file merging capability."""
    import os
    import tempfile
    
    designate_holidays = st.checkbox(
        "Brug for at angive feriedage" if lang == 'da' else "Use to designate holidays",
        value=False
    )
    
    if designate_holidays:
        col_1, col_2 = st.columns([3,1])
        if 'holiday_list' not in st.session_state:
            st.session_state.holiday_list = load_holidays_from_json("holidays.json")
        
        with col_1:
            holiday = st.date_input(
                (get_text('add_date', lang)),
                value="today"
            )
        with col_2:
            if holiday not in st.session_state.holiday_list and st.button(get_text('save', lang)):
                st.session_state.holiday_list.append(holiday)
                save_holidays_to_json(st.session_state.holiday_list, "holidays.json")

        if st.session_state.holiday_list:
            st.write("**" + ("Valgte helligdage:" if lang == 'da' else "Selected holidays:") + "**")
            
            # Sort dates for better display
            sorted_holidays = sorted(st.session_state.holiday_list)
            
            for i, holiday_date in enumerate(sorted_holidays):
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.write(f"{holiday_date.strftime('%Y-%m-%d (%A)')}")  # Shows day of week too
                
                with col2:
                    if st.button("❌", key=f"remove_holiday_{i}", 
                            help="Fjern denne dato" if lang == 'da' else "Remove this date"):
                        st.session_state.holiday_list.remove(holiday_date)
                        save_holidays_to_json(st.session_state.holiday_list, "holidays.json")
                        st.success("Dato fjernet!" if lang == 'da' else "Date removed!")
                        st.rerun()  # Refresh to update the display
        
    # Historical schedule enable/disable
    use_historical = st.checkbox(
        "Brug historisk vagtplan data" if lang == 'da' else "Use historical schedule data",
        value=False,
        help="Aktivér for at inkludere historiske vagtdata i planlægningen" if lang == 'da' 
             else "Enable to include historical schedule data in planning"
    )
    
    historical_file_path = None
    historical_info = None
    
    if use_historical:
        st.write("**" + ("Indlæs historisk vagtplan:" if lang == 'da' else "Load historical schedule:") + "**")
        
        # File upload method selection
        upload_method = st.radio(
            "Vælg indlæsningsmetode:" if lang == 'da' else "Choose upload method:",
            ["Upload fil" if lang == 'da' else "Upload file", 
             "Angiv sti" if lang == 'da' else "Specify path"],
            horizontal=True,
            key="historical_upload_method"
        )
        
        if upload_method == ("Upload fil" if lang == 'da' else "Upload file"):
            # File uploader
            uploaded_file = st.file_uploader(
                "Vælg Excel fil med historisk vagtplan" if lang == 'da' else "Choose Excel file with historical schedule",
                type=['xlsx', 'xls'],
                help="Filen skal indeholde medarbejder-ID'er som rækker og datoer som kolonner" if lang == 'da'
                     else "File should contain employee IDs as rows and dates as columns",
                key="historical_file_uploader"
            )
            
            if uploaded_file is not None:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    historical_file_path = tmp_file.name
                
                st.success("✅ " + ("Fil uploadet succesfuldt" if lang == 'da' else "File uploaded successfully"))

                # Preview the file
                try:
                    preview_df = pd.read_excel(historical_file_path)
                    st.write("**" + ("Forhåndsvisning af fil:" if lang == 'da' else "File preview:") + "**")
                    st.dataframe(preview_df.head(), width='stretch')
                    
                    # Extract some basic info
                    num_employees = len(preview_df)
                    date_columns = [col for col in preview_df.columns[1:] 
                                  if col != preview_df.columns[0]]
                    
                    if date_columns:
                        try:
                            start_date = pd.to_datetime(date_columns[0]).date()
                            end_date = pd.to_datetime(date_columns[-1]).date()
                            historical_info = {
                                'num_employees': num_employees,
                                'start_date': start_date,
                                'end_date': end_date,
                                'num_days': len(date_columns)
                            }
                            
                            st.info(
                                f"**Historisk data:** {num_employees} medarbejdere, "
                                f"{len(date_columns)} dage ({start_date} til {end_date})"
                                if lang == 'da' else
                                f"**Historical data:** {num_employees} employees, "
                                f"{len(date_columns)} days ({start_date} to {end_date})"
                            )
                        except:
                            st.warning("Kunne ikke parse datokolonner" if lang == 'da' 
                                     else "Could not parse date columns")
                    
                except Exception as e:
                    st.error(f"Fejl ved læsning af fil: {e}" if lang == 'da' 
                           else f"Error reading file: {e}")
        
        else:
            # File path input
            historical_file_path = st.text_input(
                "Sti til historisk vagtplan fil:" if lang == 'da' else "Path to historical schedule file:",
                value="./historical_schedule.xlsx",
                help="Angiv den fulde sti til Excel-filen" if lang == 'da' 
                     else "Specify the full path to the Excel file",
                key="historical_path_input"
            )
            
            # Validate file path
            if historical_file_path and os.path.exists(historical_file_path):
                st.success("✅ " + ("Fil fundet" if lang == 'da' else "File found"))
                
                # Preview the file
                try:
                    preview_df = pd.read_excel(historical_file_path)
                    with st.expander("Vis forhåndsvisning" if lang == 'da' else "Show preview"):
                        st.dataframe(preview_df.head(), width='stretch')
                except Exception as e:
                    st.warning(f"Kunne ikke læse fil: {e}" if lang == 'da' 
                             else f"Could not read file: {e}")
            elif historical_file_path:
                st.error("❌ " + ("Fil ikke fundet" if lang == 'da' else "File not found"))
        
        # Historical schedule format help
        with st.expander("" + ("Format hjælp" if lang == 'da' else "Format help")):
            st.write("**" + ("Forventet filformat:" if lang == 'da' else "Expected file format:") + "**")
            
            example_data = {
                'Employee_ID': ['EMP001', 'EMP002', 'EMP003'],
                '2025-06-01': ['DAG', '', 'NAT'],
                '2025-06-02': ['', 'AFTEN', 'DAG'],
                '2025-06-03': ['NAT', 'DAG', '']
            }
            example_df = pd.DataFrame(example_data)
            st.dataframe(example_df, width='stretch')
            
            st.write("**" + ("Regler:" if lang == 'da' else "Rules:") + "**")
            rules = [
                "Første kolonne: Medarbejder ID'er" if lang == 'da' else "First column: Employee IDs",
                "Øvrige kolonner: Datoer i YYYY-MM-DD format" if lang == 'da' else "Other columns: Dates in YYYY-MM-DD format", 
                "Celler: Vagt ID'er (f.eks. 'DAG', 'NAT') eller tomme for fridage" if lang == 'da' else "Cells: Shift IDs (e.g. 'DAG', 'NAT') or empty for days off"
            ]
            for rule in rules:
                st.write(f"• {rule}")

    # NEW: Constraint File Merging Section
    merged_file_paths = show_constraint_file_merger_ui(lang)
      
    # Constraint testing enable/disable
    run_constraint_test = st.checkbox(
        "Kør begrænsnings test" if lang == 'da' else "Run constraint testing",
        value=False,
        help="Test hvilke begrænsninger der forårsager umulige løsninger" if lang == 'da' 
             else "Test which constraints cause infeasible solutions"
    )
    
    if run_constraint_test:
        st.write("**" + ("Test konfiguration:" if lang == 'da' else "Test configuration:") + "**")
        
        col1, col2 = st.columns(2)
        with col1:
            test_start_date = st.date_input(
                "Test " + get_text('start_date', lang),
                value=get_next_month_range()[0],
                help="Start dato for begrænsnings test" if lang == 'da' else "Start date for constraint testing"
            )
        
        with col2:
            test_end_date = st.date_input(
                "Test " + get_text('end_date', lang),
                value=get_next_month_range()[1],
                help="Slut dato for begrænsnings test" if lang == 'da' else "End date for constraint testing"
            )
        
        max_test_time = st.number_input(
            "Max tid per test (sekunder)" if lang == 'da' else "Max time per test (seconds)",
            min_value=5,
            max_value=60,
            value=10,
            help="Maksimal tid for hver enkelt test" if lang == 'da' else "Maximum time for each individual test"
        )
        
        # Validate test date range
        test_is_valid, test_error, test_num_days, test_description = validate_date_range(test_start_date, test_end_date)
        
        if not test_is_valid:
            st.error(f"Ugyldigt test dato interval: {test_error}" if lang == 'da' else f"Invalid test date range: {test_error}")
        else:
            st.info(f"Test periode: {test_description} ({test_num_days} dage)" if lang == 'da' else f"Test period: {test_description} ({test_num_days} days)")
            
            # Run constraint test button
            if st.button("" + ("Start Begrænsnings Test" if lang == 'da' else "Start Constraint Test"), type="secondary"):
                # For constraint testing, use merged constraints if available
                test_hard_constraints = None
                if merged_file_paths:
                    temp_merged = create_merged_constraint_files(merged_file_paths, lang)
                    test_hard_constraints = temp_merged.get('hard_constraints')
                
                if not test_hard_constraints:
                    test_hard_constraints = get_file_paths()['hard_constraints']
                
                run_constraint_testing_simple(
                    test_start_date,
                    test_end_date,
                    max_test_time,
                    historical_file_path if use_historical else None,
                    lang,
                    test_hard_constraints  # Pass the merged constraints file
                )

    # Show information about date range impact when historical data is used
    if use_historical and historical_info:
        st.info(
            "" + ("Med historisk data vil kalenderen blive udvidet til at inkludere både historiske og fremtidige datoer" 
                    if lang == 'da' else 
                    "With historical data, the calendar will be extended to include both historical and future dates")
        )
    
    default_start, default_end = get_next_month_range()
    
    # Date inputs
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input(
            get_text('start_date', lang),
            value=default_start,
            help="Start dag for vagtplanlægningsperioden" if lang == 'da' else "Start day of scheduling period"
        )
    
    with col2:
        end_date = st.date_input(
            get_text('end_date', lang),
            value=default_end,
            help="Sidste dag for vagtplanlægningsperioden (inklusiv)" if lang == 'da' else "Last day of scheduling period (inclusive)"
        )
    
    # Validate date range and show information
    is_valid, error_msg, num_days, description = validate_date_range(start_date, end_date)
    
    if not is_valid:
        st.error(f"{get_text('invalid_date_range', lang)}: {error_msg}")
    else:
        # Show scheduling period info
        period_info = f"**{get_text('scheduling_for', lang)}:** {description} ({num_days} {get_text('days_total', lang)})"
        
        # Add historical context if available
        if use_historical and historical_info:
            total_days = historical_info['num_days'] + num_days
            period_info += f"\n\n**📊 Udvidet kalender:**\n"
            period_info += f"• Historiske dage: {historical_info['num_days']} ({historical_info['start_date']} til {historical_info['end_date']})\n"
            period_info += f"• Nye dage: {num_days} ({start_date} til {end_date})\n"
            period_info += f"• **Total: {total_days} dage**"
            
            if lang == 'en':
                period_info = period_info.replace("Udvidet kalender:", "Extended calendar:")
                period_info = period_info.replace("Historiske dage:", "Historical days:")
                period_info = period_info.replace("Nye dage:", "New days:")
                period_info = period_info.replace("Total:", "Total:")
        
        st.info(period_info)
    
    # Model settings
    st.subheader(get_text('model_settings', lang))
    
    max_time = st.number_input(
        get_text('max_time_seconds', lang),
        min_value=1,
        max_value=7200,  # 2 hours max
        value=1800,      # 30 minutes default
        step=60,
        help="Maksimal tid i sekunder for modellen at køre" if lang == 'da' else "Maximum time in seconds for the model to run"
    )
    
    # ENHANCED: Data Files Section - now simplified when using constraint merging
    st.subheader("" + get_text('data_files', lang))
    
    # Initialize session state for uploaded files
    if 'uploaded_data_files' not in st.session_state:
        st.session_state.uploaded_data_files = {}
    
    # Get default file paths
    file_paths = get_file_paths()
    
    # File configuration - only employees and shifts when using constraint merging
    if merged_file_paths:
        st.info("🔗 " + ("Bruger sammenføjede begrænsningsfiler ovenfor" if lang == 'da' 
                        else "Using merged constraint files from above"))
        file_configs = [
            {
                'key': 'employees',
                'label': get_text('employees_file', lang),
                'default_path': file_paths['employees'],
                'file_types': ['xlsx', 'xls'],
                'help': "Excel fil med medarbejder data" if lang == 'da' else "Excel file with employee data"
            },
            {
                'key': 'shifts',
                'label': get_text('shifts_file', lang),
                'default_path': file_paths['shifts'],
                'file_types': ['xlsx', 'xls'],
                'help': "Excel fil med vagt definitioner" if lang == 'da' else "Excel file with shift definitions"
            }
        ]
    else:
        # Standard file configuration when not using constraint merging
        file_configs = [
            {
                'key': 'employees',
                'label': get_text('employees_file', lang),
                'default_path': file_paths['employees'],
                'file_types': ['xlsx', 'xls'],
                'help': "Excel fil med medarbejder data" if lang == 'da' else "Excel file with employee data"
            },
            {
                'key': 'shifts',
                'label': get_text('shifts_file', lang),
                'default_path': file_paths['shifts'],
                'file_types': ['xlsx', 'xls'],
                'help': "Excel fil med vagt definitioner" if lang == 'da' else "Excel file with shift definitions"
            },
            {
                'key': 'hard_constraints',
                'label': get_text('hard_constraints_file', lang),
                'default_path': file_paths['hard_constraints'],
                'file_types': ['xlsx', 'xls'],
                'help': "Excel fil med hårde begrænsninger" if lang == 'da' else "Excel file with hard constraints"
            },
            {
                'key': 'soft_constraints',
                'label': get_text('soft_constraints_file', lang),
                'default_path': file_paths['soft_constraints'],
                'file_types': ['xlsx', 'xls'],
                'help': "Excel fil med bløde begrænsninger" if lang == 'da' else "Excel file with soft constraints"
            }
        ]
    
    # Create file selection interface for each file
    final_file_paths = {}
    
    for config in file_configs:
        with st.expander(f"{config['label']}", expanded=False):
            # File input method selection
            method_key = f"{config['key']}_input_method"
            input_method = st.radio(
                "Vælg input metode:" if lang == 'da' else "Choose input method:",
                ["Upload fil" if lang == 'da' else "Upload file", 
                 "Angiv sti" if lang == 'da' else "Specify path"],
                horizontal=True,
                key=method_key
            )
            
            if input_method == ("Upload fil" if lang == 'da' else "Upload file"):
                # File uploader
                uploaded_file = st.file_uploader(
                    f"Vælg {config['label'].lower()}" if lang == 'da' else f"Choose {config['label'].lower()}",
                    type=config['file_types'],
                    help=config['help'],
                    key=f"{config['key']}_uploader"
                )
                
                if uploaded_file is not None:
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        temp_path = tmp_file.name
                    
                    # Store in session state
                    st.session_state.uploaded_data_files[config['key']] = temp_path
                    final_file_paths[config['key']] = "./" + uploaded_file.name
                    
                    # Test for file upload success
                    st.success("✅ " + ("Fil uploadet succesfuldt" if lang == 'da' else "File uploaded successfully"))

                    update_session_state_after_upload(config['key'], temp_path, uploaded_file, lang)

                    # Show file preview
                    try:
                        preview_df = pd.read_excel(temp_path)
                        st.write("**" + ("Forhåndsvisning:" if lang == 'da' else "Preview:") + "**")
                        st.dataframe(preview_df.head(), width='stretch')
                        
                        # Show basic info
                        st.info(f"📊 {len(preview_df)} rækker, {len(preview_df.columns)} kolonner" if lang == 'da' 
                               else f"📊 {len(preview_df)} rows, {len(preview_df.columns)} columns")
                        
                    except Exception as e:
                        st.warning(f"Kunne ikke forhåndsvise fil: {e}" if lang == 'da' 
                                 else f"Could not preview file: {e}")
                else:
                    # Use default path if no file uploaded
                    final_file_paths[config['key']] = config['default_path']
                    st.info(f"🔄 Bruger standard sti: {config['default_path']}" if lang == 'da' 
                           else f"🔄 Using default path: {config['default_path']}")
            
            else:
                # File path input
                file_path = st.text_input(
                    f"Sti til {config['label'].lower()}:" if lang == 'da' else f"Path to {config['label'].lower()}:",
                    value=config['default_path'],
                    help=config['help'],
                    key=f"{config['key']}_path_input"
                )
                
                final_file_paths[config['key']] = file_path
                
                # Validate file path
                if file_path and os.path.exists(file_path):
                    st.success("✅ " + ("Fil fundet" if lang == 'da' else "File found"))
                    
                    # Show file preview
                    try:
                        preview_df = pd.read_excel(file_path)
                        with st.expander("Vis forhåndsvisning" if lang == 'da' else "Show preview"):
                            st.dataframe(preview_df.head(), width='stretch')
                            st.info(f"📊 {len(preview_df)} rækker, {len(preview_df.columns)} kolonner" if lang == 'da' 
                                   else f"📊 {len(preview_df)} rows, {len(preview_df.columns)} columns")
                    except Exception as e:
                        st.warning(f"Kunne ikke læse fil: {e}" if lang == 'da' 
                                 else f"Could not read file: {e}")
                elif file_path:
                    st.error("❌ " + ("Fil ikke fundet" if lang == 'da' else "File not found"))

    # Handle constraint file paths - either from merging or standard selection
    if merged_file_paths:
        # Create merged constraint files
        merged_constraint_files = create_merged_constraint_files(merged_file_paths, lang)
        
        # Add constraint file paths to final_file_paths
        final_file_paths['hard_constraints'] = merged_constraint_files.get('hard_constraints', get_file_paths()['hard_constraints'])
        final_file_paths['soft_constraints'] = merged_constraint_files.get('soft_constraints', get_file_paths()['soft_constraints'])
    else:
        # Use standard paths if not merging constraints
        if 'hard_constraints' not in final_file_paths:
            final_file_paths['hard_constraints'] = file_paths['hard_constraints']
        if 'soft_constraints' not in final_file_paths:
            final_file_paths['soft_constraints'] = file_paths['soft_constraints']

    # Save updated file paths (only for non-merged, non-uploaded files)
    standard_paths = {
        'employees': final_file_paths['employees'],
        'shifts': final_file_paths['shifts'],
        'hard_constraints': file_paths['hard_constraints'] if merged_file_paths else final_file_paths['hard_constraints'],
        'soft_constraints': file_paths['soft_constraints'] if merged_file_paths else final_file_paths['soft_constraints']
    }

    # Save paths if they differ from the loaded ones (only for specified paths, not uploads)
    if standard_paths != file_paths and not merged_file_paths:
        save_file_paths(standard_paths)
    
    # Show summary of selected files
    with st.expander("📋 " + ("Valgte filer oversigt" if lang == 'da' else "Selected files summary"), expanded=True):
        for key in ['employees', 'shifts', 'hard_constraints', 'soft_constraints']:
            if key in final_file_paths:
                file_path = final_file_paths[key]
                label = {
                    'employees': get_text('employees_file', lang),
                    'shifts': get_text('shifts_file', lang),
                    'hard_constraints': get_text('hard_constraints_file', lang),
                    'soft_constraints': get_text('soft_constraints_file', lang)
                }[key]
                
                if merged_file_paths and key in ['hard_constraints', 'soft_constraints']:
                    st.write(f"• **{label}:** 🔗 Merged constraint file")
                elif file_path in st.session_state.uploaded_data_files.values():
                    st.write(f"• **{label}:** 📤 Uploaded file")
                else:
                    file_status = "✅ Found" if os.path.exists(file_path) else "❌ Not found"
                    st.write(f"• **{label}:** {file_path} ({file_status})")
    
    # Run button (only enabled if date range is valid and all files exist)
    all_files_exist = all(os.path.exists(final_file_paths[key]) for key in final_file_paths)
    
    run_button_text = get_text('run_model', lang)
    if use_historical:
        run_button_text += ""  # Add icon to indicate historical data usage
    if merged_file_paths:
        run_button_text += ""  # Add icon to indicate constraint merging
    
    if not all_files_exist:
        st.error("❌ " + ("Nogle filer eksisterer ikke" if lang == 'da' else "Some files do not exist"))
    
    if st.button(run_button_text, type="primary", disabled=not (is_valid and all_files_exist)):
        if is_valid and all_files_exist:
            holidays = load_holidays_from_json("holidays.json")
            holidays = [holiday.isoformat() for holiday in holidays]
            run_enhanced_scheduling_model_with_historical(
                start_date,
                end_date,
                max_time,
                final_file_paths['employees'],
                final_file_paths['shifts'],
                final_file_paths['hard_constraints'],
                final_file_paths['soft_constraints'],
                historical_file_path if use_historical else None,
                lang,
                holidays=holidays
            )
        elif not is_valid:
            st.error(get_text('invalid_date_range', lang))
        else:
            st.error("❌ " + ("Alle filer skal eksistere før kørsel" if lang == 'da' else "All files must exist before running"))

# =============================================================================
# TOOLS TAB IMPLEMENTATION
# Add this to your UI.py file
# =============================================================================

def show_tools_tab(lang):
    """Display the tools interface with schedule converter functionality."""
    st.header("Tools" if lang == 'en' else "Værktøjer")
    st.markdown("Utility tools for data processing" if lang == 'en' else "Hjælpeværktøjer til databehandling")
    
    # Schedule Converter Section
    st.subheader("📄 " + ("Schedule Converter" if lang == 'en' else "Vagtplan Konverter"))
    
    use_converter = st.checkbox(
        "Use Schedule Converter" if lang == 'en' else "Brug Vagtplan Konverter",
        help="Convert finished schedules to historical format and replace nicknames with employee IDs" if lang == 'en' 
             else "Konverter færdige vagtplaner til historisk format og erstat kaldenavne med medarbejder-ID'er"
    )
    
    if use_converter:
        # File upload section
        st.markdown("**Step 1:** " + ("Select schedule file to convert" if lang == 'en' else "Vælg vagtplan fil at konvertere"))
        
        uploaded_file = st.file_uploader(
            "Choose finished schedule file" if lang == 'en' else "Vælg færdig vagtplan fil",
            type=['xlsx', 'xls'],
            help="Upload the finished schedule file (dates as rows, shifts as columns, nicknames in cells)" if lang == 'en'
                 else "Upload den færdige vagtplan fil (datoer som rækker, vagter som kolonner, kaldenavne i celler)"
        )
        
        if uploaded_file is not None:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                temp_input_path = tmp_file.name
            
            try:
                # Preview the uploaded file
                st.markdown("**File Preview:**")
                preview_df = pd.read_excel(temp_input_path, nrows=5)
                st.dataframe(preview_df)
                
                # Step 2: Convert using schedule_converter
                st.markdown("**Step 2:** " + ("Convert schedule format" if lang == 'en' else "Konverter vagtplan format"))
                
                if st.button("🔄 " + ("Convert Schedule" if lang == 'en' else "Konverter Vagtplan")):
                    try:
                        # Import and use schedule_converter
                        from core.schedule_converter import convert_schedule_format
                        
                        # Create temporary output file
                        with tempfile.NamedTemporaryFile(delete=False, suffix='_converted.xlsx') as tmp_output:
                            temp_output_path = tmp_output.name
                        
                        # Run conversion
                        with st.spinner("Converting schedule format..." if lang == 'en' else "Konverterer vagtplan format..."):
                            success = convert_schedule_format(temp_input_path, temp_output_path)
                        
                        if success:
                            st.success("✅ " + ("Schedule converted successfully!" if lang == 'en' else "Vagtplan konverteret succesfuldt!"))
                            
                            # Step 3: Replace nicknames with IDs
                            st.markdown("**Step 3:** " + ("Replace nicknames with employee IDs" if lang == 'en' else "Erstat kaldenavne med medarbejder-ID'er"))
                            
                            # Load the converted file
                            converted_df = pd.read_excel(temp_output_path)
                            
                            # Load employee data for nickname-to-ID mapping
                            employees_file = get_file_paths()['employees']
                            employees_df = load_employees(employees_file)
                            
                            if not employees_df.empty:
                                # Create nickname to ID mapping
                                nickname_to_id = {}
                                if 'nickname' in employees_df.columns and 'ID' in employees_df.columns:
                                    for _, row in employees_df.iterrows():
                                        if pd.notna(row['nickname']) and pd.notna(row['ID']):
                                            nickname_to_id[str(row['nickname']).strip()] = str(row['ID']).strip()
                                
                                if nickname_to_id:
                                    # Replace nicknames with IDs in all columns except the first (employee names)
                                    modified_df = converted_df.copy()
                                    date_columns = [col for col in converted_df.columns if col != converted_df.columns[0]]
                                    
                                    replacements_made = 0
                                    for col in date_columns:
                                        for nickname, emp_id in nickname_to_id.items():
                                            mask = modified_df[col].astype(str).str.strip() == nickname
                                            if mask.any():
                                                modified_df.loc[mask, col] = emp_id
                                                replacements_made += mask.sum()
                                    
                                    st.info(f"📝 Made {replacements_made} nickname → ID replacements" if lang == 'en' 
                                           else f"📝 Foretog {replacements_made} kaldenavn → ID erstatninger")
                                    
                                    # Preview the changes
                                    st.markdown("**Preview with ID replacements:**")
                                    st.dataframe(modified_df.head())
                                    
                                    # Step 4: Save output file
                                    st.markdown("**Step 4:** " + ("Save converted file" if lang == 'en' else "Gem konverteret fil"))
                                    
                                    col1, col2 = st.columns([3, 1])
                                    with col1:
                                        output_filename = st.text_input(
                                            "Output filename" if lang == 'en' else "Output filnavn",
                                            value=f"historical_schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                            help="Name for the converted file" if lang == 'en' else "Navn på den konverterede fil"
                                        )
                                    
                                    with col2:
                                        if st.button("💾 " + ("Save File" if lang == 'en' else "Gem Fil")):
                                            try:
                                                # Ensure .xlsx extension
                                                if not output_filename.endswith('.xlsx'):
                                                    output_filename += '.xlsx'
                                                
                                                # Save the modified dataframe
                                                modified_df.to_excel(output_filename, index=False)
                                                
                                                st.success(f"✅ " + (f"File saved as: {output_filename}" if lang == 'en' 
                                                                   else f"Fil gemt som: {output_filename}"))
                                                
                                                # Offer download
                                                with open(output_filename, 'rb') as f:
                                                    st.download_button(
                                                        label="📥 " + ("Download File" if lang == 'en' else "Download Fil"),
                                                        data=f.read(),
                                                        file_name=output_filename,
                                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                                    )
                                                
                                            except Exception as e:
                                                st.error(f"❌ " + ("Error saving file:" if lang == 'en' else "Fejl ved gemning af fil:") + f" {str(e)}")
                                
                                else:
                                    st.warning("⚠️ " + ("No nickname mappings found in employee data" if lang == 'en' 
                                                       else "Ingen kaldenavn tilknytninger fundet i medarbejderdata"))
                                    
                                    # Still offer to save without ID replacement
                                    output_filename = st.text_input(
                                        "Output filename" if lang == 'en' else "Output filnavn",
                                        value=f"historical_schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                                    )
                                    
                                    if st.button("💾 " + ("Save File (without ID replacement)" if lang == 'en' else "Gem Fil (uden ID erstatning)")):
                                        try:
                                            if not output_filename.endswith('.xlsx'):
                                                output_filename += '.xlsx'
                                            
                                            converted_df.to_excel(output_filename, index=False)
                                            st.success(f"✅ " + (f"File saved as: {output_filename}" if lang == 'en' 
                                                               else f"Fil gemt som: {output_filename}"))
                                        except Exception as e:
                                            st.error(f"❌ " + ("Error saving file:" if lang == 'en' else "Fejl ved gemning af fil:") + f" {str(e)}")
                            
                            else:
                                st.warning("⚠️ " + ("No employee data found for nickname mapping" if lang == 'en' 
                                                   else "Ingen medarbejderdata fundet til kaldenavn tilknytning"))
                        
                        else:
                            st.error("❌ " + ("Failed to convert schedule" if lang == 'en' else "Kunne ikke konvertere vagtplan"))
                    
                    except ImportError:
                        st.error("❌ " + ("schedule_converter module not found" if lang == 'en' else "schedule_converter modul ikke fundet"))
                    except Exception as e:
                        st.error(f"❌ " + ("Error during conversion:" if lang == 'en' else "Fejl under konvertering:") + f" {str(e)}")
            
            except Exception as e:
                st.error(f"❌ " + ("Error reading file:" if lang == 'en' else "Fejl ved læsning af fil:") + f" {str(e)}")
            
            finally:
                # Clean up temporary files
                try:
                    if 'temp_input_path' in locals():
                        os.unlink(temp_input_path)
                    if 'temp_output_path' in locals():
                        os.unlink(temp_output_path)
                except:
                    pass  # Ignore cleanup errors

def run_enhanced_scheduling_model_with_historical(start_date, end_date, max_time, employees_file, shifts_file, 
                                                hard_constraints_file, soft_constraints_file, historical_file_path, lang, holidays=None):
    """Run the enhanced scheduling model by calling main.py with real-time progress updates."""
    import os
    import tempfile
    import json
    import subprocess
    import time
    
    # Create configuration file with all parameters
    config = {
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'employees_file': employees_file,
        'shifts_file': shifts_file,
        'hard_constraints_file': hard_constraints_file,
        'soft_constraints_file': soft_constraints_file,
        'historical_file_path': historical_file_path,
        'max_time': max_time,
        'holidays': holidays
    }
    
    # Write config to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f)
        config_file = f.name
    
    # Create UI elements for progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    time_remaining_container = st.empty()
    
    # Container for detailed output (initially hidden)
    output_container = st.empty()
    
    try:
        # Use Popen for real-time communication
        from pathlib import Path
        BASEDIR = Path(__file__).resolve().parent
        core_main = BASEDIR / "core" / "main.py"
        process = subprocess.Popen(
            [sys.executable, "-u", str(core_main), "--config", config_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        
        detailed_output = []  # Collect all output for final display
        solver_started = False
        
        # Read output line by line in real-time
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
                
            line = output.strip()
            if not line:
                continue
                
            # Collect all output for detailed view
            detailed_output.append(line)
                
            if line.startswith('PROGRESS:'):
                # Parse progress update: PROGRESS:percentage:message[:TIME_REMAINING:seconds]
                parts = line.split(':')
                if len(parts) >= 3:
                    try:
                        percentage = int(parts[1])
                        message = parts[2]
                        
                        # Update progress bar and status
                        progress_bar.progress(percentage)
                        status_text.text(message)
                        
                        # Handle time remaining display
                        if len(parts) >= 5 and parts[3] == 'TIME_REMAINING':
                            solver_started = True
                            time_remaining = int(parts[4])
                            
                            if time_remaining > 0:
                                # Format time nicely
                                minutes = time_remaining // 60
                                seconds = time_remaining % 60
                                
                                if minutes > 0:
                                    time_text = f"⏱️ {minutes}m {seconds}s remaining"
                                else:
                                    time_text = f"⏱️ {seconds}s remaining"
                                    
                                time_remaining_container.markdown(f"**{time_text}**")
                            else:
                                time_remaining_container.markdown("**⏱️ Finalizing solution...**")
                                
                        elif percentage >= 75 and not solver_started:
                            # We're in solver phase but no specific time info yet
                            time_remaining_container.markdown("**⏱️ Solver starting...**")
                        elif percentage >= 95:
                            # Clear time remaining during output generation
                            time_remaining_container.empty()
                            
                    except (ValueError, IndexError) as e:
                        # Malformed progress line, just ignore
                        print(f"Could not parse progress line: {line}")
                        
            elif line.startswith('✅') or line.startswith('❌'):
                # Important status messages
                if line.startswith('✅'):
                    status_text.text("✅ " + line.split('✅', 1)[1].strip())
                else:
                    status_text.text("❌ " + line.split('❌', 1)[1].strip())
        
        # Get final result
        return_code = process.poll()
        
        # Clear time remaining display
        time_remaining_container.empty()
        
        # Handle final results
        if return_code == 0:
            # Success!
            status_text.text("")
            progress_bar.progress(100)
            st.success(get_text('model_success', lang) + " 🎉")
            
            # Enhanced success message for historical integration
            if historical_file_path:
                st.success("📊 " + ("Historisk vagtplan succesfuldt integreret!" if lang == 'da' 
                                  else "Historical schedule successfully integrated!"))
            
            # Show output file location
            st.info("📄 " + ("Output gemt til schedule_output.xlsx" if lang == 'da' 
                           else "Output saved to schedule_output.xlsx"))
            
            # Show detailed output in an expander
            with st.expander("📋 " + ("Detaljeret log" if lang == 'da' else "Detailed log")):
                # Filter out progress lines for cleaner display
                clean_output = [line for line in detailed_output if not line.startswith('PROGRESS:')]
                if clean_output:
                    st.text('\n'.join(clean_output))
                else:
                    st.text("No detailed output available")
                    
        else:
            # Error occurred
            status_text.text("")
            st.error(get_text('model_error', lang))
            
            # Show error details
            stderr_output = process.stderr.read()
            if stderr_output.strip():
                with st.expander("❌ " + ("Fejl detaljer" if lang == 'da' else "Error details")):
                    st.text(stderr_output)
            
            # Also show stdout for context
            if detailed_output:
                with st.expander("📋 " + ("Program output" if lang == 'en' else "Program output")):
                    clean_output = [line for line in detailed_output if not line.startswith('PROGRESS:')]
                    st.text('\n'.join(clean_output))
    
    except subprocess.TimeoutExpired:
        # This shouldn't happen since we handle timeout in main.py, but just in case
        status_text.text("")
        time_remaining_container.empty()
        st.error("Model timed out unexpectedly" if lang == 'en' else "Model fik uventet timeout")
        try:
            process.kill()
        except:
            pass
        
    except Exception as e:
        # Unexpected error in UI code
        status_text.text("")
        time_remaining_container.empty()
        st.error(f"{get_text('model_error', lang)}: {e}")
        
        # Show traceback for debugging
        import traceback
        with st.expander("🐛 " + ("Debug information" if lang == 'en' else "Debug information")):
            st.text(traceback.format_exc())
    
    finally:
        # Clean up config file
        if os.path.exists(config_file):
            try:
                os.remove(config_file)
            except:
                pass  # Ignore cleanup errors
        
        # Clean up uploaded historical file if it was temporary
        if historical_file_path and (historical_file_path.startswith('/tmp') or 'temp' in historical_file_path.lower()):
            try:
                if os.path.exists(historical_file_path):
                    os.remove(historical_file_path)
            except:
                pass  # Ignore cleanup errors

# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    """Main application entry point."""
    apply_custom_styling()
    
    # Language selection in sidebar
    if 'language' not in st.session_state:
        st.session_state.language = 'da'
    
    with st.sidebar:
        st.subheader(get_text('language', st.session_state.language))
        new_language = st.selectbox(
            "Language",
            options=['da', 'en'],
            format_func=lambda x: get_text('danish' if x == 'da' else 'english', x),
            index=0 if st.session_state.language == 'da' else 1,
            key="language_selector",
            label_visibility="hidden"
        )
        
        if new_language != st.session_state.language:
            st.session_state.language = new_language
            st.rerun()
    
    lang = st.session_state.language
    
    # Main header
    st.title(get_text('app_title', lang))
    st.markdown(get_text('app_subtitle', lang))
    
    # Create tabs - NOW WITH 5 TABS
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        get_text('employees_tab', lang),
        get_text('shifts_tab', lang),
        get_text('constraints_tab', lang),
        get_text('run_model_tab', lang),
        get_text('tools_tab', lang)  # NEW TAB
    ])
    
    with tab1:
        show_employees_tab(lang)
    
    with tab2:
        show_shifts_tab(lang)
    
    with tab3:
        show_constraints_tab(lang)
    
    with tab4:
        show_run_model_tab(lang)
    
    with tab5:  # NEW TAB
        show_tools_tab(lang)


if __name__ == "__main__":
    main()