{
    'name': 'AI Marketing Assistant',
    'version': '1.0',
    'category': 'Marketing',
    'summary': 'AI-powered marketing assistant with chat functionality',
    'depends': ['base', 'web', 'utm'],
    'external_dependencies': {
        'python': ['psycopg2'],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/marketing_data_views.xml',
        'views/database_test_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ai_marketing_assistant/static/src/css/marketing_chat.css',
            'ai_marketing_assistant/static/src/js/marketing_chat.js',
            'ai_marketing_assistant/static/src/xml/marketing_chat_templates.xml',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
