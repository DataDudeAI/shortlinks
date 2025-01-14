def load_ui_styles():
    return """
    <style>
        /* Main theme colors */
        :root {
            --primary-color: #10B981; /* Default green for text and primary elements */
            --secondary-color: #0891b2; /* Accent teal */
            --background-color: #f9fafb; /* Light grey background */
            --text-color: var(--primary-color); /* Green text by default */
            --border-color: #cbd5e1; /* Soft border color */
            --shadow-color: rgba(0, 0, 0, 0.05); /* Light shadow */
        }

        /* Dark theme colors */
        [data-theme="dark"] {
            --background-color: #111827;
            --text-color: #10B981;
            --border-color: #374151;
            --shadow-color: rgba(0, 0, 0, 0.4);
        }

        /* Common styles */
        body {
            font-family: 'Inter', sans-serif;
            background: var(--background-color);
            color: var(--text-color);
            margin: 0;
            padding: 0;
            line-height: 1.5;
        }

        .main-header {
            padding: 2rem 0;
            text-align: center;
            background: var(--background-color);
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 2rem;
        }

        .main-header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--text-color);
            margin: 0;
        }

        /* Card styles */
        .card {
            background: var(--background-color);
            border: 1px solid var(--border-color);
            border-radius: 0.75rem;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 4px var(--shadow-color);
        }

        /* Button styles */
        .btn-primary {
            background-color: var(--primary-color);
            color: white;
            padding: 0.75rem 1.25rem;
            border-radius: 0.5rem;
            border: none;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 600;
            transition: background-color 0.2s, transform 0.2s;
        }

        .btn-primary:hover {
            background-color: #059669;
            transform: translateY(-2px);
        }

        /* Activity item styles */
        .activity-item {
            display: flex;
            align-items: center;
            padding: 1rem;
            background: var(--background-color);
            border: 1px solid var(--border-color);
            border-radius: 0.75rem;
            margin-bottom: 0.75rem;
            box-shadow: 0 1px 3px var(--shadow-color);
        }

        .activity-icon {
            font-size: 1.5rem;
            margin-right: 1rem;
            color: var(--primary-color);
        }

        .activity-content {
            flex: 1;
        }

        .activity-title {
            font-weight: 600;
            margin-bottom: 0.5rem;
        }

        .activity-meta {
            font-size: 0.875rem;
            color: var(--secondary-color);
        }

        /* Form styles */
        .form-group {
            margin-bottom: 1.25rem;
        }

        .form-label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
            color: var(--text-color);
        }

        .form-input {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid var(--border-color);
            border-radius: 0.5rem;
            background: var(--background-color);
            color: var(--text-color);
        }

        .form-input:focus {
            outline: none;
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.4);
        }

        /* Login page styles */
        .login-container {
            max-width: 400px;
            margin: 5rem auto;
            padding: 2rem;
            background: var(--background-color);
            border-radius: 0.75rem;
            box-shadow: 0 4px 8px var(--shadow-color);
        }

        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }

        .login-header h2 {
            font-size: 1.75rem;
            font-weight: 600;
            color: var(--text-color);
        }
    </style>
    """
