from fasthtml.common import *


def marketing_page():
    return Html(
        Head(
            Meta(charset='UTF-8'),
            Meta(name='viewport', content='width=device-width, initial-scale=1.0, viewport-fit=cover'),
            Meta(name='theme-color', content='#1a4d6d'),
            Meta(name='description', content='Premium home cleaning across Sydney. Trusted, police-checked cleaners. Instant online booking. No lock-in contracts.'),
            Meta(name='apple-mobile-web-app-capable', content='yes'),
            Meta(name='apple-mobile-web-app-status-bar-style', content='default'),
            Meta(name='apple-mobile-web-app-title', content='Filo Cleaning'),
            Title('Filo Cleaning Services – Premium Home Cleaning in Sydney'),
            Link(rel='stylesheet', href='/css/styles.css'),
            Link(rel='manifest', href='/manifest.json'),
        ),
        Body(
            # Announcement Banner
            Div(
                Div(
                    Div(
                        Span('✨ New Customer Offer: ', cls='banner-badge'),
                        Span('Get 15% off your first deep clean this month with code '),
                        Span('SPRING15', cls='banner-code'),
                        A('Book Now →', href='#quote', cls='banner-link'),
                        
                        # Duplicated for seamless marquee loop
                        Span('✨ New Customer Offer: ', cls='banner-badge', style='margin-left: 2rem;'),
                        Span('Get 15% off your first deep clean this month with code '),
                        Span('SPRING15', cls='banner-code'),
                        A('Book Now →', href='#quote', cls='banner-link'),
                        cls='marquee-inner'
                    ),
                    cls='banner-content marquee'
                ),
                cls='announcement-banner'
            ),
            # Navbar — must be a direct Body child for sticky to work across the full page
            Nav(
                Div(
                    A(
                        Div(
                            Img(src='/images/logo.png', alt='Logo', cls='nav-logo-img'),
                            'Filo Cleaning Services',
                            cls='logo'
                        ),
                        href='/',
                        style='text-decoration: none;'
                    ),
                    Button(
                        Span(cls='bar'),
                        Span(cls='bar'),
                        Span(cls='bar'),
                        cls='hamburger',
                        id='hamburger',
                        aria_label='Toggle menu',
                        aria_expanded='false',
                    ),
                    Div(
                        A('How It Works', href='#how-it-works'),
                        A('Services', href='#services'),
                        A('Get Quote', href='#quote'),
                        A('Track Booking', href='/booking/lookup'),
                        A('Book Now', href='/book', cls='cta-link'),
                        cls='nav-links',
                        id='nav-links',
                    ),
                    cls='nav-container',
                ),
                cls='navbar',
                id='navbar',
            ),

            # Hero
            Section(
                Div(
                    Div(
                        H1('Premium Home Cleaning Across ', Span('Sydney.', cls='hero-highlight')),
                        P('Trusted, police-checked cleaners. Instant online booking. No lock-in contracts.', cls='hero-subtitle'),
                        Div(
                            Button('Get Instant Quote', onclick="document.getElementById('quote').scrollIntoView({behavior:'smooth'})", cls='btn btn-primary'),
                            Button('Book Now', onclick="window.location.href='/book'", cls='btn btn-secondary'),
                            cls='hero-buttons',
                        ),
                        Div(
                            Span('✔ Fully Insured', cls='badge'),
                            Span('✔ Satisfaction Guarantee', cls='badge'),
                            Span('✔ 5-Star Rated Across Sydney', cls='badge'),
                            cls='trust-badges',
                        ),
                        cls='hero-text-content',
                    ),
                    Div(
                        Img(
                            src='https://images.unsplash.com/photo-1581578731548-c64695cc6952?auto=format&fit=crop&q=80&w=1400',
                            alt='Immaculately clean and bright living room',
                            cls='hero-image'
                        ),
                        cls='hero-image-wrapper'
                    ),
                    cls='hero-content',
                ),
                cls='hero',
            ),

            # How It Works
            Section(
                Div(
                    H2('How It Works'),
                    Div(
                        Div(
                            Div('1', cls='step-number'),
                            H3('Choose Your Service'),
                            P('Select regular, deep, or end-of-lease cleaning.'),
                            cls='step',
                        ),
                        Div(
                            Div('2', cls='step-number'),
                            H3('Pick Date & Time'),
                            P('Flexible scheduling that fits your lifestyle.'),
                            cls='step',
                        ),
                        Div(
                            Div('3', cls='step-number'),
                            H3('Relax'),
                            P('Our trusted Sydney cleaners handle the rest.'),
                            cls='step',
                        ),
                        cls='steps-container',
                    ),
                    cls='container',
                ),
                id='how-it-works',
                cls='how-it-works section-full',
            ),

            # Services
            Section(
                Div(
                    H2('Cleaning Services Designed for Sydney Homes'),
                    Div(
                        Div(
                            Img(src='https://loremflickr.com/600/400/livingroom,clean/all', alt='Regular Cleaning', cls='service-img'),
                            Div(
                                H3('Regular Cleaning'),
                                P('Perfect for weekly or fortnightly upkeep.'),
                                Div('From $89', cls='price'),
                                Button('Book Now', onclick="window.location.href='/book'", cls='btn btn-outline btn-full'),
                                cls='service-content'
                            ),
                            cls='service-card'
                        ),
                        Div(
                            Img(src='https://loremflickr.com/600/400/bathroom,clean/all', alt='Deep Cleaning', cls='service-img'),
                            Div(
                                H3('Deep Cleaning'),
                                P('For seasonal refresh or detailed reset.'),
                                Div('From $189', cls='price'),
                                Button('Book Now', onclick="window.location.href='/book'", cls='btn btn-outline btn-full'),
                                cls='service-content'
                            ),
                            cls='service-card'
                        ),
                        Div(
                            Img(src='https://loremflickr.com/600/400/kitchen,clean/all', alt='End of Lease', cls='service-img'),
                            Div(
                                H3('End of Lease Cleaning'),
                                P('Bond-back guarantee service for rentals.'),
                                Div('From $299', cls='price'),
                                Button('Book Now', onclick="window.location.href='/book'", cls='btn btn-outline btn-full'),
                                cls='service-content'
                            ),
                            cls='service-card'
                        ),
                        Div(
                            Img(src='https://loremflickr.com/600/400/house,clean/all', alt='Move In', cls='service-img'),
                            Div(
                                H3('Move-In Cleaning'),
                                P('Start fresh right in your new home.'),
                                Div('From $249', cls='price'),
                                Button('Book Now', onclick="window.location.href='/book'", cls='btn btn-outline btn-full'),
                                cls='service-content'
                            ),
                            cls='service-card'
                        ),
                        Div(
                            Img(src='https://loremflickr.com/600/400/apartment,clean/all', alt='Apartment', cls='service-img'),
                            Div(
                                H3('Apartment Cleaning'),
                                P('Designed for CBD and high-rise living.'),
                                Div('From $79', cls='price'),
                                Button('Book Now', onclick="window.location.href='/book'", cls='btn btn-outline btn-full'),
                                cls='service-content'
                            ),
                            cls='service-card'
                        ),
                        cls='services-grid',
                    ),
                    cls='container',
                ),
                id='services',
                cls='services section-full',
            ),

            # Quote Calculator
            Section(
                Div(
                    H2('Get Your Instant Quote'),
                    Div(
                        Div(
                            Div(
                                Label('Bedrooms', fr='bedrooms'),
                                Select(
                                    Option('1', value='1'),
                                    Option('2', value='2', selected=''),
                                    Option('3', value='3'),
                                    Option('4', value='4'),
                                    Option('5+', value='5'),
                                    id='bedrooms', onchange='updateQuote()',
                                ),
                                cls='input-group',
                            ),
                            Div(
                                Label('Bathrooms', fr='bathrooms'),
                                Select(
                                    Option('1', value='1'),
                                    Option('2', value='2', selected=''),
                                    Option('3', value='3'),
                                    Option('4+', value='4'),
                                    id='bathrooms', onchange='updateQuote()',
                                ),
                                cls='input-group',
                            ),
                            Div(
                                Label('Service Type', fr='service-type'),
                                Select(
                                    Option('Regular Cleaning', value='regular'),
                                    Option('Deep Cleaning', value='deep'),
                                    Option('End of Lease', value='endlease'),
                                    id='service-type', onchange='updateQuote()',
                                ),
                                cls='input-group',
                            ),
                            cls='calculator-inputs',
                        ),
                        Div(
                            Label('Add-ons'),
                            Div(
                                Label(Input(type='checkbox', value='oven', onchange='updateQuote()'), 'Oven Cleaning (+$35)', cls='addon-item'),
                                Label(Input(type='checkbox', value='carpet', onchange='updateQuote()'), 'Carpet Cleaning (+$50)', cls='addon-item'),
                                Label(Input(type='checkbox', value='balcony', onchange='updateQuote()'), 'Balcony (+$25)', cls='addon-item'),
                                Label(Input(type='checkbox', value='windows', onchange='updateQuote()'), 'Windows (+$40)', cls='addon-item'),
                                cls='addon-list',
                            ),
                            cls='addons',
                        ),
                        Div(
                            Div('Estimated Price', cls='price-label'),
                            Div('$195', id='price-value', cls='price-value'),
                            Button('Book Now', onclick="window.location.href='/book'", cls='btn btn-primary btn-full'),
                            cls='price-display',
                        ),
                        cls='calculator',
                    ),
                    cls='container',
                ),
                id='quote',
                cls='quote-calculator section-full',
            ),

            # Why Choose Us
            Section(
                Div(
                    H2('Why Sydney Chooses Filo Cleaning Services'),
                    P('We don\'t just clean surfaces—we restore comfort and peace of mind to your home.', cls='section-desc'),
                    Div(
                        Div(Span('✓', cls='checkmark'), P('Experienced & vetted cleaners'), cls='benefit'),
                        Div(Span('✓', cls='checkmark'), P('Transparent pricing'), cls='benefit'),
                        Div(Span('✓', cls='checkmark'), P('Eco-friendly products available'), cls='benefit'),
                        Div(Span('✓', cls='checkmark'), P('No hidden fees'), cls='benefit'),
                        Div(Span('✓', cls='checkmark'), P('Easy rescheduling'), cls='benefit'),
                        cls='benefits',
                    ),
                    cls='container',
                ),
                cls='why-choose-us section-full',
            ),

            # Recurring Plans
            Section(
                Div(
                    H2('Save With Recurring Cleaning'),
                    Div(
                        Div(H3('Weekly'), Div('Save 10%', cls='discount'), P('Best for busy professionals', cls='plan-desc'), cls='plan'),
                        Div(H3('Fortnightly'), Div('Save 7%', cls='discount'), P('Perfect balance', cls='plan-desc'), cls='plan'),
                        Div(H3('Monthly'), Div('Save 5%', cls='discount'), P('Flexible option', cls='plan-desc'), cls='plan'),
                        cls='subscription-plans',
                    ),
                    P('Cancel anytime. No contracts.', cls='plan-note'),
                    cls='container',
                ),
                cls='subscription-offer section-full',
            ),

            # Service Areas
            Section(
                H2("Servicing Sydney's Most Popular Areas"),
                Div(
                    Div(
                        Img(src='https://loremflickr.com/600/400/sydney,city/all', alt='Sydney CBD', cls='location-img'),
                        Div(
                            H3('Sydney CBD & Surrounds'),
                            Ul(Li('Surry Hills'), Li('Darlinghurst'), Li('Pyrmont'), Li('Zetland')),
                            cls='location-content'
                        ),
                        cls='location-card'
                    ),
                    Div(
                        Img(src='https://loremflickr.com/600/400/sydney,beach/all', alt='Eastern Suburbs', cls='location-img'),
                        Div(
                            H3('Eastern Suburbs'),
                            Ul(Li('Bondi'), Li('Coogee'), Li('Double Bay'), Li('Randwick')),
                            cls='location-content'
                        ),
                        cls='location-card'
                    ),
                    Div(
                        Img(src='https://loremflickr.com/600/400/sydney,street/all', alt='Inner West', cls='location-img'),
                        Div(
                            H3('Inner West'),
                            Ul(Li('Newtown'), Li('Glebe'), Li('Balmain'), Li('Marrickville')),
                            cls='location-content'
                        ),
                        cls='location-card'
                    ),
                    Div(
                        Img(src='https://loremflickr.com/600/400/sydney,suburb/all', alt='North Shore', cls='location-img'),
                        Div(
                            H3('North Shore'),
                            Ul(Li('Chatswood'), Li('Mosman'), Li('Lane Cove'), Li('Hornsby')),
                            cls='location-content'
                        ),
                        cls='location-card'
                    ),
                    cls='locations-grid',
                ),
                id='locations',
                cls='locations section-constrained',
            ),

            # Reviews
            Section(
                Div(
                    H2('Trusted by Sydney Homeowners'),
                    Div(
                        Div(
                            Div(
                                Img(src='https://images.unsplash.com/photo-1438761681033-6461ffad8d80?auto=format&fit=crop&w=150&h=150&q=80', alt='Sarah M.', cls='review-avatar'),
                                Div(
                                    H4('Sarah M.'),
                                    Span('Bondi Beach', cls='review-location'),
                                    cls='review-author-info'
                                ),
                                cls='review-header'
                            ),
                            Div('⭐⭐⭐⭐⭐', cls='stars'),
                            P('"The cleaners were punctual, professional, and left my apartment sparkling. Highly recommended!"', cls='review-text'),
                            cls='review-card'
                        ),
                        Div(
                            Div(
                                Img(src='https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=150&h=150&q=80', alt='David L.', cls='review-avatar'),
                                Div(
                                    H4('David L.'),
                                    Span('Surry Hills', cls='review-location'),
                                    cls='review-author-info'
                                ),
                                cls='review-header'
                            ),
                            Div('⭐⭐⭐⭐⭐', cls='stars'),
                            P('"Booking was seamless. The deep clean service exceeded my expectations. Will use again."', cls='review-text'),
                            cls='review-card'
                        ),
                        Div(
                            Div(
                                Img(src='https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=150&h=150&q=80', alt='Emma T.', cls='review-avatar'),
                                Div(
                                    H4('Emma T.'),
                                    Span('Chatswood', cls='review-location'),
                                    cls='review-author-info'
                                ),
                                cls='review-header'
                            ),
                            Div('⭐⭐⭐⭐⭐', cls='stars'),
                            P('"Finally a cleaning company I can trust. The attention to detail is fantastic."', cls='review-text'),
                            cls='review-card'
                        ),
                        cls='reviews-grid',
                    ),
                    cls='container',
                ),
                id='reviews',
                cls='reviews section-full',
            ),

            # Final CTA
            Section(
                Div(
                    H2('Ready for a Cleaner Home?'),
                    Button('Book Your Cleaning Today', onclick="window.location.href='/book'", cls='btn btn-primary btn-large'),
                    P('Instant confirmation. Secure payment. Stress-free experience.', cls='cta-text'),
                    cls='container',
                ),
                id='contact',
                cls='final-cta section-full',
            ),

            # Footer
            Footer(
                Div(
                    Div(
                        H3('Filo Cleaning Services', cls='footer-brand-name'),
                        P('Premium home cleaning across Sydney. Trusted, police-checked professionals dedicated to making your space shine.', cls='footer-brand-desc'),
                        Div(
                            A('IG', href='#', cls='social-link', aria_label='Instagram'),
                            A('FB', href='#', cls='social-link', aria_label='Facebook'),
                            A('IN', href='#', cls='social-link', aria_label='LinkedIn'),
                            cls='social-links'
                        ),
                        cls='footer-brand',
                    ),
                    Div(
                        H4('Services'),
                        Ul(
                            Li(A('Regular Cleaning', href='#services')),
                            Li(A('Deep Cleaning', href='#services')),
                            Li(A('End of Lease', href='#services')),
                        ),
                        cls='footer-section',
                    ),
                    Div(
                        H4('Company'),
                        Ul(
                            Li(A('How It Works', href='#how-it-works')),
                            Li(A('Pricing', href='#quote')),
                            Li(A('Track My Booking', href='/booking/lookup')),
                            Li(A('FAQ', href='#')),
                            Li(A('Contact Us', href='mailto:hello@filocleaning.com.au')),
                        ),
                        cls='footer-section',
                    ),
                    Div(
                        H4('Service Areas'),
                        Ul(
                            Li(A('Sydney CBD', href='#')),
                            Li(A('Eastern Suburbs', href='#')),
                            Li(A('Inner West', href='#')),
                            Li(A('North Shore', href='#')),
                        ),
                        cls='footer-section',
                    ),
                    cls='footer-content',
                ),
                Div(P('© 2025 Filo Cleaning Services. All rights reserved.'), cls='footer-bottom'),
                cls='footer',
            ),

            Script(src='/js/script.js'),
        ),
        lang='en',
    )
