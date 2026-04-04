"""
Seed script to populate database with sample data for CR8TIVEIQ website.
Run with: python manage.py shell < seed_data.py
Or: python seed_data.py
"""

import os
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.core.models import Testimonial
from apps.services.models import Service
from apps.portfolio.models import PortfolioProject
from apps.blog.models import BlogArticle
from apps.contact.models import ContactInquiry, NewsletterSubscriber

User = get_user_model()


def create_superuser():
    """Create admin superuser if not exists."""
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@cr8tiveiq.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        print("✓ Superuser created (username: admin, password: admin123)")
    else:
        print("✓ Superuser already exists")


def seed_testimonials():
    """Seed testimonials."""
    testimonials_data = [
        {
            'client_name': 'Jessica Anderson',
            'company': 'Miro',
            'role': 'CFO',
            'testimonial_text': 'Our new website has received rave reviews from customers, and we\'ve seen a significant increase in traffic and conversions. The team at CR8TIVEIQ truly understood our vision.',
            'rating': 5,
            'order': 1,
        },
        {
            'client_name': 'Chloe Hayes',
            'company': 'Airtable',
            'role': 'CEO',
            'testimonial_text': 'Their team\'s expertise in digital marketing helped us reach new heights of success, and brought our brand to life in ways we never imagined possible.',
            'rating': 5,
            'order': 2,
        },
        {
            'client_name': 'Paul Brown',
            'company': 'Clubhouse',
            'role': 'CEO',
            'testimonial_text': 'They took the time to understand our goals and challenges, delivered a comprehensive strategy that has transformed our brand identity and market presence.',
            'rating': 5,
            'order': 3,
        },
        {
            'client_name': 'Sarah Mitchell',
            'company': 'TechStart',
            'role': 'Marketing Director',
            'testimonial_text': 'Working with CR8TIVEIQ was a game-changer for our startup. Their creative approach and attention to detail exceeded all our expectations.',
            'rating': 5,
            'order': 4,
        },
        {
            'client_name': 'Michael Chen',
            'company': 'DesignHub',
            'role': 'Founder',
            'testimonial_text': 'The level of professionalism and creativity is unmatched. They delivered our project on time and the results speak for themselves.',
            'rating': 5,
            'order': 5,
        },
    ]
    
    for data in testimonials_data:
        Testimonial.objects.get_or_create(
            client_name=data['client_name'],
            defaults=data
        )
    print(f"✓ Seeded {len(testimonials_data)} testimonials")


def seed_services():
    """Seed services."""
    services_data = [
        {
            'title': 'Brand Management',
            'slug': 'brand-management',
            'short_description': 'Develop a powerful brand identity that resonates with your target audience and sets you apart from competitors in today\'s crowded marketplace.',
            'description': '''
                <h2>Transform Your Brand Identity</h2>
                <p>In today's competitive landscape, a strong brand identity is more than just a logo—it's the essence of who you are as a business. Our team of brand strategists and designers works closely with you to develop a customized brand strategy that aligns with your business objectives and resonates deeply with your target audience.</p>
                
                <h3>Our Brand Management Process</h3>
                <p>We follow a proven methodology that ensures your brand stands out and creates lasting impressions:</p>
                <ol>
                    <li><strong>Discovery & Research:</strong> We dive deep into your business, industry, competitors, and target audience to understand what makes you unique.</li>
                    <li><strong>Strategy Development:</strong> We craft a comprehensive brand strategy including positioning, messaging, and visual direction.</li>
                    <li><strong>Identity Design:</strong> Our designers create a cohesive visual identity that brings your brand to life.</li>
                    <li><strong>Implementation:</strong> We help you roll out your new brand across all touchpoints with detailed guidelines.</li>
                </ol>
                
                <h3>What We Deliver</h3>
                <ul>
                    <li><strong>Brand Strategy & Positioning:</strong> Clear positioning that differentiates you from competitors</li>
                    <li><strong>Visual Identity Design:</strong> Logo, color palette, typography, and graphic elements</li>
                    <li><strong>Brand Guidelines:</strong> Comprehensive style guides ensuring consistency</li>
                    <li><strong>Brand Messaging:</strong> Voice, tone, and key messages that resonate</li>
                    <li><strong>Brand Collateral:</strong> Business cards, letterheads, and marketing materials</li>
                    <li><strong>Digital Assets:</strong> Social media templates, email signatures, and web graphics</li>
                </ul>
                
                <h3>Why Brand Management Matters</h3>
                <p>A well-managed brand builds trust, creates emotional connections, and drives customer loyalty. It's the foundation of all your marketing efforts and the key to standing out in a crowded market. Let us help you create a brand that not only looks great but also drives real business results.</p>
                
                <blockquote>
                    <p>"Your brand is what other people say about you when you're not in the room." - Jeff Bezos</p>
                </blockquote>
            ''',
            'icon': 'brand',
            'order': 1,
        },
        {
            'title': 'Social Media Management',
            'slug': 'social-media-management',
            'short_description': 'Engage your audience and grow your online presence with strategic social media management that drives real business results.',
            'description': '''
                <h2>Amplify Your Social Presence</h2>
                <p>Social media is where your customers spend their time, and it's where your brand needs to be. At CR8TIVEIQ, we specialize in delivering tailored social media solutions that drive engagement, build communities, and help our clients achieve their business goals.</p>
                
                <h3>Our Social Media Services</h3>
                <p>We offer comprehensive social media management that covers every aspect of your online presence:</p>
                
                <h4>Strategy Development</h4>
                <p>We create data-driven social media strategies tailored to your business goals, target audience, and industry. Our strategies include platform selection, content themes, posting schedules, and KPI tracking.</p>
                
                <h4>Content Creation</h4>
                <ul>
                    <li>Eye-catching graphics and videos</li>
                    <li>Engaging captions and copy</li>
                    <li>Stories and reels for maximum reach</li>
                    <li>User-generated content campaigns</li>
                    <li>Influencer collaboration content</li>
                </ul>
                
                <h4>Community Management</h4>
                <p>We don't just post and ghost. Our team actively engages with your audience, responds to comments and messages, and builds meaningful relationships that turn followers into customers.</p>
                
                <h4>Paid Social Advertising</h4>
                <ul>
                    <li>Facebook and Instagram ads</li>
                    <li>LinkedIn sponsored content</li>
                    <li>Twitter promoted tweets</li>
                    <li>TikTok advertising campaigns</li>
                    <li>A/B testing and optimization</li>
                </ul>
                
                <h4>Analytics & Reporting</h4>
                <p>We provide detailed monthly reports showing your growth, engagement rates, reach, and ROI. Our insights help you understand what's working and where to invest more.</p>
                
                <h3>Platforms We Manage</h3>
                <p>Instagram • Facebook • LinkedIn • Twitter • TikTok • Pinterest • YouTube</p>
                
                <h3>Results You Can Expect</h3>
                <ul>
                    <li>Increased brand awareness and reach</li>
                    <li>Higher engagement rates</li>
                    <li>More website traffic and conversions</li>
                    <li>Stronger community and customer loyalty</li>
                    <li>Better customer insights and feedback</li>
                </ul>
            ''',
            'icon': 'social',
            'order': 2,
        },
        {
            'title': 'Graphic Design',
            'slug': 'graphic-design',
            'short_description': 'Eye-catching designs that capture attention, communicate your message effectively, and leave lasting impressions on your audience.',
            'description': '''
                <h2>Visual Excellence That Drives Results</h2>
                <p>Great design is more than just aesthetics—it's about communication, emotion, and action. Our award-winning design team creates eye-catching visuals that capture attention and communicate your message effectively across all mediums, from print to digital.</p>
                
                <h3>Our Design Philosophy</h3>
                <p>We believe that every design element should serve a purpose. Our approach combines creativity with strategy, ensuring that every visual we create not only looks stunning but also drives your business objectives forward.</p>
                
                <h3>Design Services We Offer</h3>
                
                <h4>Brand Identity Design</h4>
                <ul>
                    <li>Logo design and variations</li>
                    <li>Brand style guides</li>
                    <li>Color palette development</li>
                    <li>Typography selection</li>
                    <li>Icon and graphic element creation</li>
                </ul>
                
                <h4>Marketing Collateral</h4>
                <ul>
                    <li>Brochures and flyers</li>
                    <li>Posters and banners</li>
                    <li>Business cards and stationery</li>
                    <li>Presentation templates</li>
                    <li>Trade show materials</li>
                </ul>
                
                <h4>Digital Graphics</h4>
                <ul>
                    <li>Social media graphics and templates</li>
                    <li>Web banners and ads</li>
                    <li>Email newsletter designs</li>
                    <li>Digital advertisements</li>
                    <li>App and UI graphics</li>
                </ul>
                
                <h4>Infographics & Data Visualization</h4>
                <p>Transform complex data into engaging visual stories that are easy to understand and share. Perfect for reports, presentations, and social media.</p>
                
                <h4>Packaging Design</h4>
                <p>Stand out on the shelf with packaging that not only protects your product but also tells your brand story and attracts customers.</p>
                
                <h4>Print Design</h4>
                <ul>
                    <li>Magazine and book layouts</li>
                    <li>Annual reports</li>
                    <li>Catalogs and lookbooks</li>
                    <li>Signage and environmental graphics</li>
                </ul>
                
                <h3>Our Design Process</h3>
                <ol>
                    <li><strong>Brief & Discovery:</strong> Understanding your goals, audience, and requirements</li>
                    <li><strong>Research & Inspiration:</strong> Exploring trends and gathering creative inspiration</li>
                    <li><strong>Concept Development:</strong> Creating initial design concepts and directions</li>
                    <li><strong>Refinement:</strong> Iterating based on your feedback</li>
                    <li><strong>Finalization:</strong> Delivering print-ready and web-optimized files</li>
                </ol>
                
                <h3>Why Choose Our Design Team</h3>
                <p>Our designers combine creativity with strategic thinking to deliver visuals that not only look great but also drive results. We stay current with design trends while ensuring your brand remains timeless and distinctive.</p>
            ''',
            'icon': 'design',
            'order': 3,
        },
        {
            'title': 'Web Development',
            'slug': 'web-development',
            'short_description': 'Build fast, responsive, and beautiful websites that deliver exceptional user experiences and drive conversions for your business.',
            'description': '''
                <h2>Modern Web Solutions That Perform</h2>
                <p>Your website is often the first impression customers have of your business. We build fast, responsive, and beautiful websites that deliver exceptional user experiences and drive conversions. Our development team combines technical expertise with creative design to create web solutions that work as hard as you do.</p>
                
                <h3>Our Web Development Services</h3>
                
                <h4>Custom Website Development</h4>
                <p>Tailored websites built from the ground up to meet your specific business needs. We use modern frameworks and best practices to ensure your site is fast, secure, and scalable.</p>
                <ul>
                    <li>Responsive design that works on all devices</li>
                    <li>Clean, maintainable code</li>
                    <li>SEO-friendly architecture</li>
                    <li>Fast loading times</li>
                    <li>Accessibility compliance (WCAG)</li>
                </ul>
                
                <h4>E-Commerce Platforms</h4>
                <p>Powerful online stores that make it easy for customers to browse, shop, and checkout. We build e-commerce solutions that drive sales and provide seamless shopping experiences.</p>
                <ul>
                    <li>Product catalog management</li>
                    <li>Secure payment processing</li>
                    <li>Inventory management</li>
                    <li>Order tracking and fulfillment</li>
                    <li>Customer accounts and wishlists</li>
                    <li>Analytics and reporting</li>
                </ul>
                
                <h4>Progressive Web Applications (PWAs)</h4>
                <p>Combine the best of web and mobile apps with PWAs that work offline, send push notifications, and provide app-like experiences without requiring downloads.</p>
                
                <h4>Content Management Systems (CMS)</h4>
                <p>Easy-to-use CMS solutions that let you update your website content without technical knowledge. We work with:</p>
                <ul>
                    <li>WordPress</li>
                    <li>Django CMS</li>
                    <li>Contentful</li>
                    <li>Custom CMS solutions</li>
                </ul>
                
                <h4>API Development & Integration</h4>
                <p>Connect your website with third-party services, mobile apps, and internal systems through robust API development and integration.</p>
                
                <h3>Technologies We Use</h3>
                <p><strong>Frontend:</strong> React, Vue.js, Next.js, HTML5, CSS3, Tailwind CSS, JavaScript/TypeScript</p>
                <p><strong>Backend:</strong> Django, Node.js, Python, PostgreSQL, MongoDB, Redis</p>
                <p><strong>Cloud & DevOps:</strong> AWS, Google Cloud, Docker, CI/CD pipelines</p>
                
                <h3>Our Development Process</h3>
                <ol>
                    <li><strong>Discovery & Planning:</strong> Understanding requirements and creating technical specifications</li>
                    <li><strong>Design & Prototyping:</strong> Creating wireframes and interactive prototypes</li>
                    <li><strong>Development:</strong> Building your website with clean, efficient code</li>
                    <li><strong>Testing:</strong> Rigorous QA across devices and browsers</li>
                    <li><strong>Launch:</strong> Deploying to production with monitoring</li>
                    <li><strong>Maintenance:</strong> Ongoing support and updates</li>
                </ol>
                
                <h3>Performance Guaranteed</h3>
                <p>We optimize every website for speed, security, and search engines. Our sites consistently achieve high scores on Google PageSpeed Insights and Core Web Vitals.</p>
                
                <h3>Post-Launch Support</h3>
                <p>We don't disappear after launch. Our team provides ongoing maintenance, security updates, and technical support to keep your website running smoothly.</p>
            ''',
            'icon': 'web',
            'order': 4,
        },
        {
            'title': 'Content Creation',
            'slug': 'content-creation',
            'short_description': 'Engaging content that tells your brand story, connects with your audience, and drives action across all digital platforms.',
            'description': '''
                <h2>Compelling Content That Converts</h2>
                <p>Content is the currency of the digital age. Whether it's a blog post, video, or social media caption, great content tells your brand story and connects with your audience in meaningful ways. Our content creators craft messages that resonate with your target audience, drive engagement, and support your business objectives.</p>
                
                <h3>Our Content Services</h3>
                
                <h4>Blog Posts & Articles</h4>
                <p>Well-researched, SEO-optimized blog content that establishes your authority, educates your audience, and drives organic traffic.</p>
                <ul>
                    <li>Industry insights and thought leadership</li>
                    <li>How-to guides and tutorials</li>
                    <li>Case studies and success stories</li>
                    <li>News and trend analysis</li>
                    <li>Product reviews and comparisons</li>
                </ul>
                
                <h4>Website Copy & Landing Pages</h4>
                <p>Persuasive copy that converts visitors into customers. We write clear, compelling website content that guides users through your sales funnel.</p>
                <ul>
                    <li>Homepage and about page copy</li>
                    <li>Service and product descriptions</li>
                    <li>Landing pages for campaigns</li>
                    <li>Call-to-action optimization</li>
                    <li>Value propositions and messaging</li>
                </ul>
                
                <h4>Email Marketing Campaigns</h4>
                <p>Engaging email content that nurtures leads and drives conversions. From welcome sequences to promotional campaigns, we create emails that get opened and clicked.</p>
                <ul>
                    <li>Newsletter content</li>
                    <li>Promotional emails</li>
                    <li>Drip campaigns</li>
                    <li>Abandoned cart sequences</li>
                    <li>Re-engagement campaigns</li>
                </ul>
                
                <h4>Video Scripts & Production</h4>
                <p>From concept to final cut, we create video content that captures attention and tells your story effectively.</p>
                <ul>
                    <li>Explainer videos</li>
                    <li>Product demos</li>
                    <li>Customer testimonials</li>
                    <li>Brand stories</li>
                    <li>Social media videos</li>
                </ul>
                
                <h4>Social Media Content</h4>
                <p>Scroll-stopping social content that engages your audience and builds community.</p>
                <ul>
                    <li>Post captions and copy</li>
                    <li>Stories and reels scripts</li>
                    <li>Hashtag strategy</li>
                    <li>Content calendars</li>
                    <li>Community engagement responses</li>
                </ul>
                
                <h4>White Papers & E-books</h4>
                <p>In-depth content that showcases your expertise and generates qualified leads.</p>
                
                <h4>Press Releases & PR Content</h4>
                <p>Professional press releases and media kits that get your news noticed.</p>
                
                <h3>Our Content Process</h3>
                <ol>
                    <li><strong>Strategy:</strong> Understanding your audience, goals, and brand voice</li>
                    <li><strong>Research:</strong> Gathering insights, data, and competitive intelligence</li>
                    <li><strong>Creation:</strong> Writing, editing, and optimizing content</li>
                    <li><strong>Review:</strong> Collaborative feedback and refinement</li>
                    <li><strong>Publishing:</strong> Scheduling and distributing content</li>
                    <li><strong>Analysis:</strong> Measuring performance and optimizing</li>
                </ol>
                
                <h3>Why Our Content Works</h3>
                <ul>
                    <li><strong>Audience-Focused:</strong> We write for your readers, not search engines</li>
                    <li><strong>SEO-Optimized:</strong> Content that ranks and drives organic traffic</li>
                    <li><strong>Brand-Aligned:</strong> Consistent voice and messaging across all content</li>
                    <li><strong>Data-Driven:</strong> Informed by analytics and performance metrics</li>
                    <li><strong>Conversion-Oriented:</strong> Every piece has a clear goal and CTA</li>
                </ul>
                
                <blockquote>
                    <p>"Content is king, but engagement is queen, and the lady rules the house." - Mari Smith</p>
                </blockquote>
            ''',
            'icon': 'content',
            'order': 5,
        },
        {
            'title': 'SEO Optimization',
            'slug': 'seo-optimization',
            'short_description': 'Improve your search engine rankings and drive organic traffic with comprehensive SEO strategies that deliver measurable results.',
            'description': '''
                <h2>Dominate Search Results</h2>
                <p>In today's digital landscape, being found online is crucial for business success. Our comprehensive SEO strategies help you improve your search engine rankings, drive qualified organic traffic, and increase conversions. We stay up-to-date with the latest search engine algorithms and best practices to ensure your website ranks well and attracts the right visitors.</p>
                
                <h3>Our SEO Services</h3>
                
                <h4>Technical SEO Audits & Optimization</h4>
                <p>We conduct thorough technical audits to identify and fix issues that may be holding your site back from ranking higher.</p>
                <ul>
                    <li>Site speed optimization</li>
                    <li>Mobile-friendliness improvements</li>
                    <li>Core Web Vitals optimization</li>
                    <li>XML sitemap creation and optimization</li>
                    <li>Robots.txt configuration</li>
                    <li>Schema markup implementation</li>
                    <li>HTTPS and security optimization</li>
                    <li>Crawl error resolution</li>
                </ul>
                
                <h4>Keyword Research & Strategy</h4>
                <p>We identify the keywords your target audience is searching for and develop a strategy to rank for them.</p>
                <ul>
                    <li>Competitor keyword analysis</li>
                    <li>Search intent mapping</li>
                    <li>Long-tail keyword opportunities</li>
                    <li>Keyword difficulty assessment</li>
                    <li>Content gap analysis</li>
                </ul>
                
                <h4>On-Page Optimization</h4>
                <p>Optimizing every element of your web pages to improve rankings and user experience.</p>
                <ul>
                    <li>Title tag and meta description optimization</li>
                    <li>Header tag structure (H1, H2, H3)</li>
                    <li>Content optimization and keyword placement</li>
                    <li>Image optimization and alt text</li>
                    <li>Internal linking strategy</li>
                    <li>URL structure optimization</li>
                    <li>Featured snippet optimization</li>
                </ul>
                
                <h4>Off-Page SEO & Link Building</h4>
                <p>Building your site's authority through high-quality backlinks and brand mentions.</p>
                <ul>
                    <li>Link building outreach campaigns</li>
                    <li>Guest posting opportunities</li>
                    <li>Digital PR and brand mentions</li>
                    <li>Broken link building</li>
                    <li>Competitor backlink analysis</li>
                    <li>Link profile monitoring and cleanup</li>
                </ul>
                
                <h4>Content Optimization</h4>
                <p>Creating and optimizing content that ranks well and provides value to your audience.</p>
                <ul>
                    <li>Content strategy development</li>
                    <li>SEO content writing</li>
                    <li>Content refresh and updates</li>
                    <li>Topic cluster creation</li>
                    <li>E-E-A-T optimization (Experience, Expertise, Authoritativeness, Trustworthiness)</li>
                </ul>
                
                <h4>Local SEO</h4>
                <p>Dominate local search results and attract nearby customers.</p>
                <ul>
                    <li>Google Business Profile optimization</li>
                    <li>Local citation building</li>
                    <li>Review management and generation</li>
                    <li>Local content creation</li>
                    <li>NAP consistency (Name, Address, Phone)</li>
                    <li>Local link building</li>
                </ul>
                
                <h4>E-Commerce SEO</h4>
                <p>Specialized SEO for online stores to increase product visibility and sales.</p>
                <ul>
                    <li>Product page optimization</li>
                    <li>Category page optimization</li>
                    <li>Product schema markup</li>
                    <li>Faceted navigation optimization</li>
                    <li>User-generated content optimization</li>
                </ul>
                
                <h3>Our SEO Process</h3>
                <ol>
                    <li><strong>Audit & Analysis:</strong> Comprehensive review of your current SEO status</li>
                    <li><strong>Strategy Development:</strong> Custom SEO roadmap based on your goals</li>
                    <li><strong>Implementation:</strong> Executing technical and content optimizations</li>
                    <li><strong>Monitoring:</strong> Tracking rankings, traffic, and conversions</li>
                    <li><strong>Reporting:</strong> Monthly reports with insights and recommendations</li>
                    <li><strong>Optimization:</strong> Continuous improvement based on data</li>
                </ol>
                
                <h3>What You Can Expect</h3>
                <ul>
                    <li>Increased organic search visibility</li>
                    <li>Higher rankings for target keywords</li>
                    <li>More qualified organic traffic</li>
                    <li>Improved conversion rates</li>
                    <li>Better user experience</li>
                    <li>Sustainable long-term growth</li>
                </ul>
                
                <h3>SEO Tools We Use</h3>
                <p>We leverage industry-leading tools to deliver the best results: Google Search Console, Google Analytics, Ahrefs, SEMrush, Screaming Frog, and more.</p>
                
                <h3>Transparent Reporting</h3>
                <p>We provide detailed monthly reports showing your progress, including rankings, traffic, conversions, and ROI. You'll always know exactly how your SEO investment is performing.</p>
            ''',
            'icon': 'seo',
            'order': 6,
        },
    ]
    
    for data in services_data:
        Service.objects.get_or_create(
            slug=data['slug'],
            defaults=data
        )
    print(f"✓ Seeded {len(services_data)} services")


def seed_portfolio():
    """Seed portfolio projects."""
    services = list(Service.objects.all())
    
    # Update category choices to match model
    projects_data = [
        {
            'title': 'Modern E-Commerce Platform',
            'slug': 'modern-ecommerce-platform',
            'category': 'websites',
            'description': '<p>A cutting-edge e-commerce platform built with modern technologies, featuring seamless user experience and powerful admin capabilities.</p><p>We implemented advanced features including real-time inventory management, secure payment processing, and personalized product recommendations.</p>',
            'client_name': 'ShopTech Inc.',
            'timeline': '3 months',
            'is_featured': True,
        },
        {
            'title': 'Brand Identity Design',
            'slug': 'brand-identity-design',
            'category': 'graphics',
            'description': '<p>Complete brand identity overhaul for a growing tech startup, including logo design, color palette, typography, and brand guidelines.</p><p>The new identity reflects the company\'s innovative spirit and positions them as industry leaders.</p>',
            'client_name': 'InnovateTech',
            'timeline': '2 months',
            'is_featured': True,
        },
        {
            'title': 'Social Media Campaign',
            'slug': 'social-media-campaign',
            'category': 'social_media',
            'description': '<p>Comprehensive social media strategy and execution that increased engagement by 300% and grew followers by 150% in 6 months.</p><p>Included content creation, community management, and paid advertising campaigns.</p>',
            'client_name': 'FitLife Wellness',
            'timeline': '6 months',
            'is_featured': False,
        },
        {
            'title': 'Product Launch Video',
            'slug': 'product-launch-video',
            'category': 'video',
            'description': '<p>High-impact product launch video for a fintech startup, focusing on storytelling and brand messaging.</p><p>The video achieved over 1 million views within the first week and significantly boosted product awareness.</p>',
            'client_name': 'PayFlow',
            'timeline': '1 month',
            'is_featured': True,
        },
        {
            'title': 'Digital Ad Campaign',
            'slug': 'digital-ad-campaign',
            'category': 'ads',
            'description': '<p>Multi-platform digital advertising campaign that generated 500% ROI and acquired 10,000 new customers.</p><p>Included Google Ads, Facebook Ads, and Instagram advertising with A/B testing and optimization.</p>',
            'client_name': 'GrowthCo',
            'timeline': '4 months',
            'is_featured': False,
        },
    ]
    
    for data in projects_data:
        project, created = PortfolioProject.objects.get_or_create(
            slug=data['slug'],
            defaults=data
        )
        if created and services:
            # Add random services to project
            project.services_used.add(*services[:3])
    
    print(f"✓ Seeded {len(projects_data)} portfolio projects")


def seed_blog():
    """Seed blog articles."""
    # Get admin user
    admin_user = User.objects.filter(is_superuser=True).first()
    
    # Blog articles data
    articles_data = [
        {
            'title': '10 Web Design Trends to Watch in 2026',
            'slug': '10-web-design-trends-2026',
            'summary': 'Discover the latest web design trends that will shape the digital landscape in 2026, from AI-powered personalization to immersive 3D elements.',
            'content': '<p>The web design landscape is constantly evolving, and 2026 promises to bring exciting new trends that will reshape how we create digital experiences.</p><h2>1. AI-Powered Personalization</h2><p>Artificial intelligence is revolutionizing how websites adapt to individual users, creating truly personalized experiences that increase engagement and conversions.</p><h2>2. Immersive 3D Elements</h2><p>Three-dimensional graphics and animations are becoming more accessible and performant, allowing designers to create engaging visual experiences without sacrificing load times.</p><h2>3. Micro-Interactions</h2><p>Small, delightful animations that respond to user actions are becoming essential for creating memorable user experiences.</p><p>Stay ahead of the curve by incorporating these trends into your next project and watch your engagement metrics soar.</p>',
            'category': 'Design',
            'tags': ['Web Design', 'UI/UX', 'Technology'],
            'is_published': True,
        },
        {
            'title': 'The Complete Guide to SEO in 2026',
            'slug': 'complete-guide-seo-2026',
            'summary': 'Everything you need to know about search engine optimization and how to rank higher in search results with modern SEO strategies.',
            'content': '<p>Search engine optimization continues to be crucial for online success. This comprehensive guide covers everything from technical SEO to content strategy.</p><h2>Understanding Search Intent</h2><p>Modern SEO is all about understanding what users are really looking for and providing the best possible answer. Search engines have become incredibly sophisticated at interpreting user intent.</p><h2>Technical SEO Fundamentals</h2><p>From site speed to mobile optimization, technical SEO forms the foundation of your search visibility. Core Web Vitals are now a ranking factor you can\'t ignore.</p><h2>Content Strategy</h2><p>Creating high-quality, relevant content that answers user questions is more important than ever. Focus on E-E-A-T: Experience, Expertise, Authoritativeness, and Trustworthiness.</p>',
            'category': 'Marketing',
            'tags': ['SEO', 'Content Marketing', 'Technology'],
            'is_published': True,
        },
        {
            'title': 'Building Scalable React Applications',
            'slug': 'building-scalable-react-applications',
            'summary': 'Best practices for creating maintainable and scalable React applications that can grow with your business needs.',
            'content': '<p>React has become the go-to framework for building modern web applications. Learn how to structure your React projects for long-term success.</p><h2>Component Architecture</h2><p>Proper component organization is key to maintaining a scalable codebase. Use atomic design principles to create reusable, composable components.</p><h2>State Management</h2><p>Choose the right state management solution for your application\'s needs. Context API for simple cases, Redux or Zustand for complex state.</p><h2>Performance Optimization</h2><p>Use React.memo, useMemo, and useCallback strategically to prevent unnecessary re-renders and keep your app fast.</p>',
            'category': 'Development',
            'tags': ['React', 'Web Design', 'Technology'],
            'is_published': True,
        },
        {
            'title': 'Social Media Strategy for Small Businesses',
            'slug': 'social-media-strategy-small-businesses',
            'summary': 'How small businesses can leverage social media to grow their brand and reach new customers without breaking the bank.',
            'content': '<p>Social media offers incredible opportunities for small businesses to connect with their audience and grow their brand.</p><h2>Choosing the Right Platforms</h2><p>Not all social media platforms are created equal. Focus on where your audience spends their time. B2B? LinkedIn. Visual products? Instagram. Gen Z? TikTok.</p><h2>Content Planning</h2><p>Consistency is key. Develop a content calendar and stick to it. Mix promotional content with educational and entertaining posts to keep your audience engaged.</p><h2>Engagement Tactics</h2><p>Don\'t just broadcast—engage! Respond to comments, ask questions, and create content that encourages interaction.</p>',
            'category': 'Marketing',
            'tags': ['Social Media', 'Content Marketing', 'Business'],
            'is_published': True,
        },
        {
            'title': 'The Power of Brand Storytelling',
            'slug': 'power-of-brand-storytelling',
            'summary': 'Learn how to craft compelling brand stories that resonate with your audience and create lasting emotional connections.',
            'content': '<p>Great brands don\'t just sell products—they tell stories that connect with people on an emotional level.</p><h2>Finding Your Brand Voice</h2><p>Your brand voice should be authentic and consistent across all touchpoints. It should reflect your values and resonate with your target audience.</p><h2>Creating Emotional Connections</h2><p>Stories that evoke emotion are more memorable and shareable. Use the hero\'s journey framework to structure your brand narrative.</p><h2>Authenticity Matters</h2><p>In an age of skepticism, authenticity is your greatest asset. Share real stories, admit mistakes, and show the human side of your brand.</p>',
            'category': 'Business',
            'tags': ['Branding', 'Content Marketing', 'Business'],
            'is_published': True,
        },
    ]
    
    for data in articles_data:
        tags = data.pop('tags')
        
        article, created = BlogArticle.objects.get_or_create(
            slug=data['slug'],
            defaults={
                **data,
                'author': admin_user,
                'published_at': timezone.now() - timedelta(days=30),
            }
        )
        
        if created:
            # Store tags as JSON array
            article.tags = tags
            article.save()
    
    print(f"✓ Seeded {len(articles_data)} blog articles")


def seed_contact_data():
    """Seed sample contact inquiries and newsletter subscribers."""
    # Sample inquiries
    inquiries_data = [
        {
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'phone': '+1234567890',
            'company': 'Tech Startup Inc.',
            'service_type': 'Web Development',
            'project_description': 'We need a modern website for our startup. Looking for a team that can deliver quality work with cutting-edge design and functionality.',
            'status': 'new',
        },
        {
            'name': 'Jane Smith',
            'email': 'jane.smith@example.com',
            'phone': '+1987654321',
            'company': 'Fashion Brand Co.',
            'service_type': 'Branding',
            'project_description': 'Interested in a complete brand identity redesign for our fashion company. We want to modernize our look and appeal to younger audiences.',
            'status': 'contacted',
        },
        {
            'name': 'Michael Johnson',
            'email': 'michael.j@example.com',
            'phone': '+1555123456',
            'company': 'GrowthCo',
            'service_type': 'Social Media Management',
            'project_description': 'Looking for comprehensive social media management services to increase our online presence and engagement.',
            'status': 'new',
        },
    ]
    
    for data in inquiries_data:
        ContactInquiry.objects.get_or_create(
            email=data['email'],
            defaults=data
        )
    
    print(f"✓ Seeded {len(inquiries_data)} contact inquiries")
    
    # Sample newsletter subscribers
    subscribers_data = [
        'subscriber1@example.com',
        'subscriber2@example.com',
        'subscriber3@example.com',
        'marketing@techstartup.com',
        'info@designstudio.com',
    ]
    
    for email in subscribers_data:
        NewsletterSubscriber.objects.get_or_create(
            email=email,
            defaults={'is_verified': True}
        )
    
    print(f"✓ Seeded {len(subscribers_data)} newsletter subscribers")


def main():
    """Run all seed functions."""
    print("\n" + "="*50)
    print("Starting database seeding...")
    print("="*50 + "\n")
    
    create_superuser()
    seed_testimonials()
    seed_services()
    seed_portfolio()
    seed_blog()
    seed_contact_data()
    
    print("\n" + "="*50)
    print("Database seeding completed successfully!")
    print("="*50 + "\n")
    print("Admin credentials:")
    print("  Username: admin")
    print("  Password: admin123")
    print("\nAccess admin at: http://localhost:8000/admin/")
    print("\n")


if __name__ == '__main__':
    main()
