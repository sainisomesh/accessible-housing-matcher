<?php
/**
 * Plugin Name: Housing Matcher Shortcode
 * Description: Display housing units and matches from HousingMatcher API
 * Version: 1.0.0
 * Author: Your Name
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Register shortcode: [housing_units]
 * Displays all available housing units
 */
function display_housing_units_shortcode($atts) {
    $atts = shortcode_atts(array(
        'api_url' => 'https://your-api-domain.com', // Change to your API URL
        'limit' => 10,
    ), $atts);
    
    $api_url = esc_url($atts['api_url']);
    $units = get_units_from_api($api_url);
    
    if (empty($units)) {
        return '<p>No housing units available at this time.</p>';
    }
    
    $output = '<div class="housing-units-list">';
    $count = 0;
    
    foreach ($units as $unit) {
        if ($count >= intval($atts['limit'])) {
            break;
        }
        
        $output .= '<div class="housing-unit-card">';
        
        // Property name with unit number
        $property_name = esc_html($unit['property_name'] ?? 'Unnamed Property');
        if (!empty($unit['unit_number'])) {
            $property_name .= ' - Unit ' . esc_html($unit['unit_number']);
        }
        $output .= '<h3 class="unit-property-name">' . $property_name . '</h3>';
        
        // Address
        if (!empty($unit['address'])) {
            $output .= '<p class="unit-address">📍 ' . esc_html($unit['address']) . '</p>';
        }
        
        // Rent
        if (!empty($unit['rent_display'])) {
            $output .= '<p class="unit-rent"><strong>Rent:</strong> ' . esc_html($unit['rent_display']) . '</p>';
        } elseif (!empty($unit['rent'])) {
            $output .= '<p class="unit-rent"><strong>Rent:</strong> ' . esc_html($unit['rent']) . '</p>';
        }
        
        // Contact Information (NEW - with landlord details)
        if (!empty($unit['landlord_name']) || !empty($unit['landlord_phone']) || !empty($unit['landlord_email']) || !empty($unit['contact'])) {
            $output .= '<div class="unit-contact">';
            $output .= '<strong>Contact Information:</strong><br>';
            
            // Landlord Name
            if (!empty($unit['landlord_name'])) {
                $output .= '<span class="landlord-name">Landlord: ' . esc_html($unit['landlord_name']) . '</span><br>';
            }
            
            // Phone
            if (!empty($unit['landlord_phone'])) {
                $phone = esc_html($unit['landlord_phone']);
                $output .= '<span class="landlord-phone">Phone: <a href="tel:' . esc_attr($phone) . '">' . $phone . '</a></span><br>';
            }
            
            // Email
            if (!empty($unit['landlord_email'])) {
                $email = esc_html($unit['landlord_email']);
                $output .= '<span class="landlord-email">Email: <a href="mailto:' . esc_attr($email) . '">' . $email . '</a></span><br>';
            }
            
            // Fallback to contact field if parsed fields not available
            if (empty($unit['landlord_phone']) && empty($unit['landlord_email']) && !empty($unit['contact'])) {
                $contact = esc_html($unit['contact']);
                if (strpos($contact, '@') !== false) {
                    $output .= '<span class="unit-contact-fallback">Contact: <a href="mailto:' . esc_attr($contact) . '">' . $contact . '</a></span>';
                } else {
                    $output .= '<span class="unit-contact-fallback">Contact: ' . $contact . '</span>';
                }
            }
            
            $output .= '</div>';
        }
        
        // Availability
        if (!empty($unit['availability'])) {
            $availability_class = strtolower(str_replace(' ', '-', $unit['availability']));
            $output .= '<p class="unit-availability status-' . esc_attr($availability_class) . '">';
            $output .= '<strong>Status:</strong> ' . esc_html($unit['availability']);
            if (!empty($unit['units_available']) && $unit['units_available'] > 0) {
                $output .= ' (' . intval($unit['units_available']) . ' available)';
            }
            $output .= '</p>';
        }
        
        // Accessibility Features
        if (!empty($unit['accessibility_features'])) {
            $features = explode(',', $unit['accessibility_features']);
            $output .= '<div class="unit-features">';
            $output .= '<strong>Accessibility Features:</strong> ';
            $feature_tags = array_map('trim', $features);
            $output .= '<span class="feature-tags">' . esc_html(implode(', ', $feature_tags)) . '</span>';
            $output .= '</div>';
        }
        
        // Additional fields for master units
        if (!empty($unit['income_range'])) {
            $output .= '<p class="unit-income-range"><strong>Income Range:</strong> ' . esc_html($unit['income_range']) . '</p>';
        }
        
        if (!empty($unit['age_range'])) {
            $output .= '<p class="unit-age-range"><strong>Age Range:</strong> ' . esc_html($unit['age_range']) . '</p>';
        }
        
        if (!empty($unit['transportation'])) {
            $output .= '<p class="unit-transportation"><strong>Transportation:</strong> ' . esc_html($unit['transportation']) . '</p>';
        }
        
        if (!empty($unit['notes'])) {
            $output .= '<div class="unit-notes"><strong>Notes:</strong> ' . esc_html($unit['notes']) . '</div>';
        }
        
        $output .= '</div>'; // End housing-unit-card
        $count++;
    }
    
    $output .= '</div>'; // End housing-units-list
    
    return $output;
}
add_shortcode('housing_units', 'display_housing_units_shortcode');

/**
 * Register shortcode: [housing_matches]
 * Displays matches for an applicant (requires applicant_id)
 */
function display_housing_matches_shortcode($atts) {
    $atts = shortcode_atts(array(
        'api_url' => 'https://your-api-domain.com', // Change to your API URL
        'applicant_id' => '',
    ), $atts);
    
    if (empty($atts['applicant_id'])) {
        return '<p>Please provide an applicant_id parameter.</p>';
    }
    
    $api_url = esc_url($atts['api_url']);
    $applicant_id = sanitize_text_field($atts['applicant_id']);
    
    $matches = get_matches_from_api($api_url, $applicant_id);
    
    if (empty($matches) || empty($matches['matches'])) {
        return '<p>No matches found for this applicant.</p>';
    }
    
    $output = '<div class="housing-matches-list">';
    $output .= '<h2>Your Housing Matches</h2>';
    
    // Get all units to enrich match data
    $units = get_units_from_api($api_url);
    $units_by_id = array();
    foreach ($units as $unit) {
        $units_by_id[$unit['id']] = $unit;
    }
    
    foreach ($matches['matches'] as $index => $match) {
        $unit = $units_by_id[$match['unit_id']] ?? null;
        if (!$unit) {
            continue;
        }
        
        $output .= '<div class="housing-match-card">';
        $output .= '<div class="match-header">';
        $output .= '<span class="match-rank">#' . ($index + 1) . ' Match</span>';
        $output .= '<span class="match-score">' . round($match['score'] * 100) . '% Match</span>';
        $output .= '</div>';
        
        // Property name with unit number
        $property_name = esc_html($unit['property_name'] ?? 'Unnamed Property');
        if (!empty($unit['unit_number'])) {
            $property_name .= ' - Unit ' . esc_html($unit['unit_number']);
        }
        $output .= '<h3 class="match-property-name">' . $property_name . '</h3>';
        
        // Address
        if (!empty($unit['address'])) {
            $output .= '<p class="match-address">📍 ' . esc_html($unit['address']) . '</p>';
        }
        
        // Rent
        if (!empty($unit['rent_display'])) {
            $output .= '<p class="match-rent"><strong>Rent:</strong> ' . esc_html($unit['rent_display']) . '</p>';
        }
        
        // Contact Information (NEW - with landlord details)
        if (!empty($unit['landlord_name']) || !empty($unit['landlord_phone']) || !empty($unit['landlord_email']) || !empty($unit['contact'])) {
            $output .= '<div class="match-contact">';
            $output .= '<strong>Contact Information:</strong><br>';
            
            // Landlord Name
            if (!empty($unit['landlord_name'])) {
                $output .= '<span class="landlord-name">Landlord: ' . esc_html($unit['landlord_name']) . '</span><br>';
            }
            
            // Phone
            if (!empty($unit['landlord_phone'])) {
                $phone = esc_html($unit['landlord_phone']);
                $output .= '<span class="landlord-phone">Phone: <a href="tel:' . esc_attr($phone) . '">' . $phone . '</a></span><br>';
            }
            
            // Email
            if (!empty($unit['landlord_email'])) {
                $email = esc_html($unit['landlord_email']);
                $output .= '<span class="landlord-email">Email: <a href="mailto:' . esc_attr($email) . '">' . $email . '</a></span><br>';
            }
            
            // Fallback to contact field
            if (empty($unit['landlord_phone']) && empty($unit['landlord_email']) && !empty($unit['contact'])) {
                $contact = esc_html($unit['contact']);
                if (strpos($contact, '@') !== false) {
                    $output .= '<span class="match-contact-fallback">Contact: <a href="mailto:' . esc_attr($contact) . '">' . $contact . '</a></span>';
                } else {
                    $output .= '<span class="match-contact-fallback">Contact: ' . $contact . '</span>';
                }
            }
            
            $output .= '</div>';
        }
        
        // Match reasons
        if (!empty($match['reasons'])) {
            $output .= '<div class="match-reasons">';
            $output .= '<strong>Why this match:</strong><ul>';
            foreach ($match['reasons'] as $reason) {
                $output .= '<li>' . esc_html($reason) . '</li>';
            }
            $output .= '</ul></div>';
        }
        
        $output .= '</div>'; // End housing-match-card
    }
    
    $output .= '</div>'; // End housing-matches-list
    
    return $output;
}
add_shortcode('housing_matches', 'display_housing_matches_shortcode');

/**
 * Fetch units from API
 */
function get_units_from_api($api_url) {
    $url = trailingslashit($api_url) . 'units';
    
    $response = wp_remote_get($url, array(
        'timeout' => 30,
        'sslverify' => true,
    ));
    
    if (is_wp_error($response)) {
        error_log('Housing Matcher API Error: ' . $response->get_error_message());
        return array();
    }
    
    $body = wp_remote_retrieve_body($response);
    $units = json_decode($body, true);
    
    if (!is_array($units)) {
        return array();
    }
    
    return $units;
}

/**
 * Fetch matches from API
 */
function get_matches_from_api($api_url, $applicant_id) {
    $url = trailingslashit($api_url) . 'match/' . urlencode($applicant_id);
    
    $response = wp_remote_get($url, array(
        'timeout' => 30,
        'sslverify' => true,
    ));
    
    if (is_wp_error($response)) {
        error_log('Housing Matcher API Error: ' . $response->get_error_message());
        return array();
    }
    
    $body = wp_remote_retrieve_body($response);
    $matches = json_decode($body, true);
    
    return $matches ?: array();
}

/**
 * Enqueue styles for housing units display
 */
function housing_matcher_styles() {
    wp_add_inline_style('wp-block-library', '
        .housing-units-list, .housing-matches-list {
            display: grid;
            gap: 1.5rem;
            margin: 2rem 0;
        }
        .housing-unit-card, .housing-match-card {
            border: 2px solid #ddd;
            border-radius: 8px;
            padding: 1.5rem;
            background: #fff;
        }
        .unit-property-name, .match-property-name {
            margin-top: 0;
            color: #0066CC;
        }
        .unit-contact, .match-contact {
            margin: 1rem 0;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 4px;
        }
        .landlord-name, .landlord-phone, .landlord-email {
            display: block;
            margin: 0.5rem 0;
        }
        .landlord-phone a, .landlord-email a {
            color: #0066CC;
            text-decoration: none;
        }
        .landlord-phone a:hover, .landlord-email a:hover {
            text-decoration: underline;
        }
        .match-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 1rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid #eee;
        }
        .match-rank {
            font-weight: bold;
            color: #0066CC;
        }
        .match-score {
            font-weight: bold;
            color: #00A896;
        }
        .match-reasons ul {
            margin: 0.5rem 0;
            padding-left: 1.5rem;
        }
        .status-available {
            color: #28A745;
        }
        .status-not-available {
            color: #DC3545;
        }
    ');
}
add_action('wp_enqueue_scripts', 'housing_matcher_styles');

