#!/usr/bin/env python3
"""
PageSpeed Insights Analyzer for Portfolio Website

This script analyzes the PageSpeed performance of all URLs in the website
by navigating through the sitemap and testing both mobile and desktop versions.
"""

import requests
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
import time
import json
from datetime import datetime
import csv
import os
from typing import List, Dict, Optional
import argparse
import dotenv

dotenv.load_dotenv()
PAGESPEED_API_KEY = os.getenv('PAGESPEED_API_KEY')


class PageSpeedAnalyzer:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the PageSpeed Analyzer
        
        Args:
            api_key: Optional PageSpeed Insights API key for higher quota
        """
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        self.urls = []
        self.results = []
        
    def fetch_sitemap_urls(self, sitemap_url: str) -> List[str]:
        """
        Recursively fetch all URLs from sitemap(s)
        
        Args:
            sitemap_url: URL of the sitemap or sitemap index
            
        Returns:
            List of all URLs found in the sitemap(s)
        """
        urls = []
        
        try:
            response = requests.get(sitemap_url, timeout=30)
            response.raise_for_status()
            
            # Parse XML
            root = ET.fromstring(response.content)
            
            # Handle sitemap index (contains references to other sitemaps)
            if 'sitemapindex' in root.tag:
                print(f"Found sitemap index at: {sitemap_url}")
                for sitemap in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap'):
                    loc_element = sitemap.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc_element is not None:
                        nested_sitemap_url = loc_element.text
                        print(f"Processing nested sitemap: {nested_sitemap_url}")
                        urls.extend(self.fetch_sitemap_urls(nested_sitemap_url))
            
            # Handle regular sitemap (contains actual URLs)
            elif 'urlset' in root.tag:
                print(f"Processing sitemap: {sitemap_url}")
                for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                    loc_element = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc_element is not None:
                        urls.append(loc_element.text)
                        
        except requests.RequestException as e:
            print(f"Error fetching sitemap {sitemap_url}: {e}")
        except ET.ParseError as e:
            print(f"Error parsing XML from {sitemap_url}: {e}")
            
        return urls
    
    def analyze_url(self, url: str, strategy: str = 'mobile') -> Optional[Dict]:
        """
        Analyze a single URL with PageSpeed Insights
        
        Args:
            url: URL to analyze
            strategy: 'mobile' or 'desktop'
            
        Returns:
            Dictionary containing analysis results or None if failed
        """
        params = {
            'url': url,
            'strategy': strategy,
            'category': ['performance', 'accessibility', 'best-practices', 'seo']
        }
        
        if self.api_key:
            params['key'] = self.api_key
            
        try:
            response = requests.get(self.base_url, params=params, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            # Extract key metrics
            lighthouse_result = data.get('lighthouseResult', {})
            audits = lighthouse_result.get('audits', {})
            categories = lighthouse_result.get('categories', {})
            
            # All category scores
            performance = categories.get('performance', {})
            accessibility = categories.get('accessibility', {})
            best_practices = categories.get('best-practices', {})
            seo = categories.get('seo', {})
            
            performance_score = performance.get('score', 0) * 100 if performance.get('score') is not None else 0
            accessibility_score = accessibility.get('score', 0) * 100 if accessibility.get('score') is not None else 0
            best_practices_score = best_practices.get('score', 0) * 100 if best_practices.get('score') is not None else 0
            seo_score = seo.get('score', 0) * 100 if seo.get('score') is not None else 0
            
            # Core Web Vitals
            fcp = audits.get('first-contentful-paint', {}).get('numericValue', 0) / 1000  # Convert to seconds
            lcp = audits.get('largest-contentful-paint', {}).get('numericValue', 0) / 1000
            cls = audits.get('cumulative-layout-shift', {}).get('numericValue', 0)
            fid = audits.get('max-potential-fid', {}).get('numericValue', 0)
            
            # Speed Index and other metrics
            speed_index = audits.get('speed-index', {}).get('numericValue', 0) / 1000
            interactive = audits.get('interactive', {}).get('numericValue', 0) / 1000
            
            result = {
                'url': url,
                'strategy': strategy,
                'performance_score': round(performance_score, 1),
                'accessibility_score': round(accessibility_score, 1),
                'best_practices_score': round(best_practices_score, 1),
                'seo_score': round(seo_score, 1),
                'first_contentful_paint': round(fcp, 2),
                'largest_contentful_paint': round(lcp, 2),
                'cumulative_layout_shift': round(cls, 3),
                'first_input_delay': round(fid, 2),
                'speed_index': round(speed_index, 2),
                'time_to_interactive': round(interactive, 2),
                'timestamp': datetime.now().isoformat()
            }
            
            return result
            
        except requests.RequestException as e:
            print(f"Error analyzing {url} ({strategy}): {e}")
            return None
        except KeyError as e:
            print(f"Error parsing response for {url} ({strategy}): {e}")
            return None
    
    def analyze_all_urls(self, sitemap_url: str, delay: float = 1.0, max_urls: Optional[int] = None):
        """
        Analyze all URLs from the sitemap for both mobile and desktop
        
        Args:
            sitemap_url: URL of the sitemap index
            delay: Delay between requests to avoid rate limiting
            max_urls: Maximum number of URLs to analyze (for testing)
        """
        print("Fetching URLs from sitemap...")
        self.urls = self.fetch_sitemap_urls(sitemap_url)
        
        if not self.urls:
            print("No URLs found in sitemap!")
            return
            
        print(f"Found {len(self.urls)} URLs to analyze")
        
        # Limit URLs for testing if specified
        if max_urls:
            self.urls = self.urls[:max_urls]
            print(f"Limited to {len(self.urls)} URLs for testing")
        
        total_requests = len(self.urls) * 2  # Mobile + Desktop
        current_request = 0
        
        for i, url in enumerate(self.urls, 1):
            print(f"\nAnalyzing URL {i}/{len(self.urls)}: {url}")
            
            # Analyze mobile
            current_request += 1
            print(f"  [{current_request}/{total_requests}] Mobile analysis...")
            mobile_result = self.analyze_url(url, 'mobile')
            if mobile_result:
                self.results.append(mobile_result)
            
            time.sleep(delay)  # Rate limiting
            
            # Analyze desktop
            current_request += 1
            print(f"  [{current_request}/{total_requests}] Desktop analysis...")
            desktop_result = self.analyze_url(url, 'desktop')
            if desktop_result:
                self.results.append(desktop_result)
            
            time.sleep(delay)  # Rate limiting
    
    def save_results(self, output_format: str = 'json', filename_prefix: str = 'pagespeed_results'):
        """
        Save results to file(s)
        
        Args:
            output_format: 'json', 'csv', or 'both'
            filename_prefix: Prefix for output files
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if output_format in ['json', 'both']:
            json_filename = f"{filename_prefix}_{timestamp}.json"
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print(f"\nResults saved to: {json_filename}")
        
        if output_format in ['csv', 'both']:
            csv_filename = f"{filename_prefix}_{timestamp}.csv"
            if self.results:
                fieldnames = self.results[0].keys()
                with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(self.results)
                print(f"Results saved to: {csv_filename}")
    
    def print_summary(self):
        """Print a summary of the analysis results"""
        if not self.results:
            print("No results to summarize!")
            return
        
        mobile_results = [r for r in self.results if r['strategy'] == 'mobile']
        desktop_results = [r for r in self.results if r['strategy'] == 'desktop']
        
        print(f"\n{'='*60}")
        print("PAGESPEED ANALYSIS SUMMARY")
        print(f"{'='*60}")
        print(f"Total URLs analyzed: {len(self.urls)}")
        print(f"Total requests made: {len(self.results)}")
        print(f"Mobile results: {len(mobile_results)}")
        print(f"Desktop results: {len(desktop_results)}")
        
        for strategy, results in [('Mobile', mobile_results), ('Desktop', desktop_results)]:
            if not results:
                continue
                
            perf_scores = [r['performance_score'] for r in results]
            acc_scores = [r['accessibility_score'] for r in results]
            bp_scores = [r['best_practices_score'] for r in results]
            seo_scores = [r['seo_score'] for r in results]
            fcp_values = [r['first_contentful_paint'] for r in results]
            lcp_values = [r['largest_contentful_paint'] for r in results]
            
            print(f"\n{strategy} Results:")
            print(f"  Performance:     Avg: {sum(perf_scores) / len(perf_scores):.1f} | Best: {max(perf_scores):.1f} | Worst: {min(perf_scores):.1f}")
            print(f"  Accessibility:   Avg: {sum(acc_scores) / len(acc_scores):.1f} | Best: {max(acc_scores):.1f} | Worst: {min(acc_scores):.1f}")
            print(f"  Best Practices:  Avg: {sum(bp_scores) / len(bp_scores):.1f} | Best: {max(bp_scores):.1f} | Worst: {min(bp_scores):.1f}")
            print(f"  SEO:             Avg: {sum(seo_scores) / len(seo_scores):.1f} | Best: {max(seo_scores):.1f} | Worst: {min(seo_scores):.1f}")
            print(f"  Average FCP: {sum(fcp_values) / len(fcp_values):.2f}s")
            print(f"  Average LCP: {sum(lcp_values) / len(lcp_values):.2f}s")


def main():
    parser = argparse.ArgumentParser(description='Analyze PageSpeed performance for all URLs in sitemap')
    parser.add_argument('--sitemap', default='https://www.maximofn.com/sitemap-index.xml',
                        help='Sitemap URL (default: https://www.maximofn.com/sitemap-index.xml)')
    parser.add_argument('--delay', type=float, default=1.0,
                        help='Delay between requests in seconds (default: 1.0)')
    parser.add_argument('--max-urls', type=int,
                        help='Maximum number of URLs to analyze (for testing)')
    parser.add_argument('--output', choices=['json', 'csv', 'both'], default='both',
                        help='Output format (default: both)')
    parser.add_argument('--prefix', default='pagespeed_results',
                        help='Output filename prefix (default: pagespeed_results)')
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = PageSpeedAnalyzer(api_key=PAGESPEED_API_KEY)
    
    print("PageSpeed Insights Analyzer for Portfolio Website")
    print(f"Sitemap URL: {args.sitemap}")
    
    try:
        # Run analysis
        analyzer.analyze_all_urls(
            sitemap_url=args.sitemap,
            delay=args.delay,
            max_urls=args.max_urls
        )
        
        # Print summary
        analyzer.print_summary()
        
        # Save results
        analyzer.save_results(
            output_format=args.output,
            filename_prefix=args.prefix
        )
        
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user")
        if analyzer.results:
            print("Saving partial results...")
            analyzer.save_results(
                output_format=args.output,
                filename_prefix=f"{args.prefix}_partial"
            )


if __name__ == "__main__":
    main()