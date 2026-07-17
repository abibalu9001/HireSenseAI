# Comprehensive skills dictionary for extraction
SKILLS_LIST = [
    # Programming Languages
    "Python", "JavaScript", "TypeScript", "Java", "C", "C++", "C#", "Go", "Rust",
    "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB", "Perl", "Bash",
    "Shell", "PowerShell", "Dart", "Lua", "Haskell", "Elixir", "Clojure", "F#",

    # Web Frontend
    "HTML", "CSS", "React", "Angular", "Vue.js", "Next.js", "Nuxt.js", "Svelte",
    "Bootstrap", "Tailwind CSS", "jQuery", "Redux", "Webpack", "Vite", "Sass",
    "LESS", "GraphQL", "REST API", "WebSockets", "Three.js", "D3.js",

    # Web Backend
    "Django", "Flask", "FastAPI", "Node.js", "Express.js", "Spring Boot", "Laravel",
    "Rails", "ASP.NET", "Gin", "Echo", "NestJS", "Strapi", "Sails.js",

    # Databases
    "MySQL", "PostgreSQL", "SQLite", "MongoDB", "Redis", "Elasticsearch",
    "Cassandra", "DynamoDB", "Oracle", "SQL Server", "MariaDB", "Firebase",
    "Supabase", "InfluxDB", "Neo4j", "Couchbase",

    # Cloud & DevOps
    "AWS", "Azure", "GCP", "Google Cloud", "Docker", "Kubernetes", "Terraform",
    "Ansible", "Jenkins", "GitHub Actions", "GitLab CI", "CircleCI", "Travis CI",
    "Nginx", "Apache", "Linux", "Ubuntu", "CentOS", "Heroku", "Vercel", "Netlify",
    "CloudFormation", "Pulumi", "Prometheus", "Grafana", "ELK Stack", "Datadog",

    # AI / ML / Data
    "Machine Learning", "Deep Learning", "Neural Networks", "NLP",
    "Natural Language Processing", "Computer Vision", "TensorFlow", "PyTorch",
    "Keras", "Scikit-learn", "Pandas", "NumPy", "Matplotlib", "Seaborn",
    "OpenCV", "NLTK", "spaCy", "Hugging Face", "Transformers", "BERT",
    "GPT", "LangChain", "LlamaIndex", "Stable Diffusion", "XGBoost", "LightGBM",
    "Random Forest", "SVM", "Reinforcement Learning", "MLOps", "Feature Engineering",
    "Data Analysis", "Data Science", "Data Engineering", "ETL", "Data Visualization",
    "Power BI", "Tableau", "Apache Spark", "Hadoop", "Kafka", "Airflow", "dbt",

    # Mobile
    "Android", "iOS", "React Native", "Flutter", "Xamarin", "Ionic",

    # Version Control & Tools
    "Git", "GitHub", "GitLab", "Bitbucket", "Jira", "Confluence", "Slack",
    "Postman", "Swagger", "VS Code", "IntelliJ", "PyCharm", "Eclipse",

    # Testing
    "Unit Testing", "Integration Testing", "Selenium", "Pytest", "Jest",
    "Cypress", "Mocha", "JUnit", "TestNG", "Postman", "Load Testing",
    "TDD", "BDD", "QA",

    # Security
    "Cybersecurity", "Penetration Testing", "OWASP", "SSL/TLS", "OAuth",
    "JWT", "LDAP", "Firewalls", "SIEM", "SOC", "Network Security",

    # Design
    "Figma", "Adobe XD", "Photoshop", "Illustrator", "UI/UX", "Wireframing",
    "Prototyping", "User Research",

    # Soft Skills (for matching)
    "Leadership", "Communication", "Problem Solving", "Team Work", "Agile",
    "Scrum", "Kanban", "Project Management", "Critical Thinking",
]

# Normalize to lowercase for matching
SKILLS_LOWER = {s.lower(): s for s in SKILLS_LIST}
