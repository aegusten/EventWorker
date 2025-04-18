INSERT INTO backend_jobposting (
    org_id, title, job_type, salary, location, requirements,
    deadline, description, image, created_at, is_active
) VALUES
(1, 'Software Engineer', 'full-time', 6500.00, 'KL Sentral, Kuala Lumpur',
 '2+ years in Python/Django, familiarity with REST APIs.',
 '2025-06-01', 'Join a growing fintech startup to build scalable backend systems.',
 NULL, NOW(), true),

(2, 'Marketing Executive', 'full-time', 4000.00, 'Bukit Bintang, Kuala Lumpur',
 'Strong understanding of social media and marketing funnels.',
 '2025-05-15', 'Drive campaigns, manage content calendars, and grow brand reach.',
 'static/jobs/job_image_2.jpg', NOW(), true),

(2, 'Clinic Receptionist', 'part-time', 2000.00, 'Cheras, Kuala Lumpur',
 'Friendly, organized, and experience with patient scheduling software.',
 '2025-06-10', 'Help manage patient intake and daily operations at a busy clinic.',
 'static/jobs/job_image_3.jpg', NOW(), true),

(1, 'Project Coordinator', 'full-time', 5000.00, 'Damansara, Kuala Lumpur',
 'Strong communication and project tracking skills.',
 '2025-05-30', 'Assist construction project managers in planning and execution.',
 'static/jobs/job_image_4.jpg', NOW(), true),

(2, 'Graphic Designer', 'volunteer', 0.00, 'Remote',
 'Adobe Suite experience, creative portfolio.',
 '2025-05-20', 'Help an NGO improve branding materials and digital media.',
 'static/jobs/job_image_5.jpg', NOW(), true),

(1, 'Customer Support Assistant', 'part-time', 2500.00, 'Bangsar, Kuala Lumpur',
 'Communication skills, email/chat support experience.',
 '2025-06-05', 'Assist customers with inquiries and technical troubleshooting.',
 'static/jobs/job_image_6.jpg', NOW(), true),

(1, 'Data Entry Clerk', 'full-time', 3000.00, 'Mont Kiara, Kuala Lumpur',
 'Fast typing, accuracy, spreadsheet skills.',
 '2025-05-22', 'Manage databases and enter bulk data for internal systems.',
 'static/jobs/job_image_7.jpg', NOW(), true),

(2, 'Event Planner', 'full-time', 4800.00, 'Jalan Ampang, Kuala Lumpur',
 'Strong coordination and vendor management experience.',
 '2025-06-01', 'Plan and execute medium-large scale corporate events.',
 'static/jobs/job_image_8.png', NOW(), true),

(2, 'Retail Assistant', 'part-time', 1800.00, 'Pavilion Mall, Kuala Lumpur',
 'Customer-friendly and punctual.',
 '2025-06-15', 'Handle POS systems, restocking, and customer service in-store.',
 'static/jobs/job_image_9.jpg', NOW(), true),

(1, 'Junior Android Developer', 'full-time', 5500.00, 'KL Eco City',
 'Kotlin, Android SDK, Git.',
 '2025-06-10', 'Build and maintain new app features in a fast-paced team.',
 'static/jobs/job_image_10.png', NOW(), true),

(3, 'Construction Site Helper', 'volunteer', 0.00, 'Setapak, Kuala Lumpur',
 'Physically fit, basic safety training.',
 '2025-05-25', 'Assist workers on-site with materials and logistics.',
 'static/jobs/job_image_11.jpg', NOW(), true),

(1, 'Finance Admin Assistant', 'part-time', 2800.00, 'Mid Valley, Kuala Lumpur',
 'Excel, data entry, invoice processing.',
 '2025-06-03', 'Support the finance team with admin and documentation.',
 'static/jobs/job_image_12.jpg', NOW(), true),

(2, 'Social Media Intern', 'volunteer', 0.00, 'Remote',
 'Familiar with Instagram, TikTok, and content creation.',
 '2025-06-05', 'Create daily posts, monitor engagement, and analyze trends.',
 'static/jobs/job_image_13.jpg', NOW(), true),

(1, 'Barista', 'part-time', 2200.00, 'Bangsar South',
 'Friendly, quick learner, coffee knowledge a bonus.',
 '2025-05-29', 'Prepare drinks, manage orders, and keep workspace tidy.',
 'static/jobs/job_image_14.jpg', NOW(), true),

(1, 'Account Manager', 'full-time', 7000.00, 'Solaris Dutamas, Kuala Lumpur',
 'Client management, sales experience, CRM skills.',
 '2025-06-08', 'Manage key accounts and build long-term client relationships.',
 'static/jobs/job_image_15.jpg', NOW(), true),

(1, 'Backend Developer (Node.js)', 'full-time', 6800.00, 'Bukit Jalil, Kuala Lumpur',
 'Node.js, Express, MongoDB',
 '2025-06-12', 'Build secure, scalable APIs for modern web apps.',
 'static/jobs/job_image_16.png', NOW(), true),

(3, 'Warehouse Assistant', 'part-time', 2000.00, 'Puchong, Selangor',
 'Able to lift boxes, punctuality.',
 '2025-05-31', 'Manage inventory and load/unload shipments.',
 'static/jobs/job_image_17.png', NOW(), true),

(2, 'Nurse Assistant', 'full-time', 4000.00, 'Setiawangsa, Kuala Lumpur',
 'Healthcare certificate, good bedside manner.',
 '2025-06-14', 'Assist nurses in patient care and records.',
 'static/jobs/job_image_18.jpg', NOW(), true),

(1, 'Business Analyst', 'full-time', 6000.00, 'Menara TM, KL',
 'SQL, reporting, stakeholder communication.',
 '2025-06-20', 'Translate business needs into data insights.',
 'static/jobs/job_image_19.jpg', NOW(), true),

(2, 'Healthcare Volunteer', 'volunteer', 0.00, 'Cheras, Kuala Lumpur', 
'Willingness to assist in healthcare-related activities.', '2025-06-01', 
'Assist in various healthcare activities such as patient care and administrative support.',
'static/jobs/volunteer.png', '2025-04-18', true);
