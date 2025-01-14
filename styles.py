def get_styles():
    return """
    <style>
        /* Main theme colors */
        :root {
            --primary-color: #10B981;
            --secondary-color: #0891b2;
            --background-color: #ffffff;
            --text-color: #1a202c;
            --border-color: #e2e8f0;
            --shadow-color: rgba(0,0,0,0.1);
        }

        /* Dark theme colors */
        [data-theme="dark"] {
            --background-color: #1a202c;
            --text-color: #f7fafc;
            --border-color: #2d3748;
            --shadow-color: rgba(0,0,0,0.3);
        }

        /* Common styles */
        .main-header {
            padding: 2rem 0;
            text-align: center;
            background: var(--background-color);
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 2rem;
        }

        .main-header h1 {
            color: var(--text-color);
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0;
        }

        /* Card styles */
        .card {
            background: var(--background-color);
            border: 1px solid var(--border-color);
            border-radius: 0.5rem;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 1px 3px var(--shadow-color);
        }

        /* Button styles */
        .btn-primary {
            background-color: var(--primary-color);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 0.375rem;
            border: none;
            cursor: pointer;
            font-size: 0.875rem;
            transition: background-color 0.2s;
        }

        .btn-primary:hover {
            background-color: #059669;
        }

        /* Activity item styles */
        .activity-item {
            display: flex;
            align-items: center;
            padding: 1rem;
            background: var(--background-color);
            border: 1px solid var(--border-color);
            border-radius: 0.5rem;
            margin-bottom: 0.5rem;
        }

        .activity-icon {
            font-size: 1.25rem;
            margin-right: 1rem;
        }

        .activity-content {
            flex: 1;
        }

        .activity-title {
            font-weight: 600;
            color: var(--text-color);
            margin-bottom: 0.25rem;
        }

        .activity-meta {
            font-size: 0.875rem;
            color: #64748b;
        }

        /* Form styles */
        .form-group {
            margin-bottom: 1rem;
        }

        .form-label {
            display: block;
            margin-bottom: 0.5rem;
            color: var(--text-color);
            font-weight: 500;
        }

        .form-input {
            width: 100%;
            padding: 0.5rem;
            border: 1px solid var(--border-color);
            border-radius: 0.375rem;
            background: var(--background-color);
            color: var(--text-color);
        }

        /* Login page styles */
        .login-container {
            max-width: 400px;
            margin: 4rem auto;
            padding: 2rem;
            background: var(--background-color);
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px var(--shadow-color);
        }

        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }

        .login-header h2 {
            color: var(--text-color);
            font-size: 1.5rem;
            font-weight: 600;
        }
    </style>
    """ 