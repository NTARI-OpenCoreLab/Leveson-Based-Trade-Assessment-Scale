#!/usr/bin/env python3
"""
Leveson-Based Trade Assessment Scale (LBTAS)
============================================

A rigorous assessment methodology for digital commerce adapted from 
Nancy Leveson's Software Assessment Scale used in aircraft software development.

Copyright (C) 2024 Network Theory Applied Research Institute
Licensed under GNU Affero General Public License v3.0

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

import json
import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime

__version__ = "1.0.0"
__author__ = "Network Theory Applied Research Institute"
__license__ = "AGPL-3.0"

class LevesonRatingSystem:
    """
    Leveson-Based Trade Assessment Scale rating system.
    
    Provides a rigorous 6-point scale (-1 to +4) for evaluating
    digital commerce interactions based on Nancy Leveson's methodology.
    """
    
    DEFAULT_CATEGORIES = ['reliability', 'usability', 'performance', 'support']
    
    RATING_DESCRIPTIONS = {
        -1: "No Trust - User was harmed, exploited, or received a product or service with no discipline or malicious intent.",
        0: "Cynical Satisfaction - Interaction fulfills a basic promise requiring little to no discipline toward user satisfaction.",
        1: "Basic Promise - Interaction meets all articulated user demands, no more.",
        2: "Basic Satisfaction - Interaction meets socially acceptable standards exceeding articulated user demands.",
        3: "No Negative Consequences - Interaction designed to prevent loss, exceed basic quality.",
        4: "Delight - Interaction anticipates the evolution of user practices and concerns post-transaction."
    }
    
    def __init__(self, storage_file: Optional[str] = None, categories: Optional[List[str]] = None):
        """
        Initialize the LBTAS rating system.
        
        Args:
            storage_file: Optional path to JSON file for persistent storage
            categories: Custom rating categories (defaults to reliability, usability, performance, support)
        """
        self.categories = categories or self.DEFAULT_CATEGORIES.copy()
        self.storage_file = storage_file
        self.exchanges = {}
        
        if self.storage_file:
            self.load_from_file()
    
    def add_exchange(self, name: str) -> None:
        """Add a new exchange to the system."""
        if name in self.exchanges:
            raise ValueError(f"Exchange '{name}' already exists.")
        
        self.exchanges[name] = {
            category: [] for category in self.categories
        }
        self.exchanges[name]['_metadata'] = {
            'created': datetime.now().isoformat(),
            'total_ratings': 0
        }
        
        if self.storage_file:
            self.save_to_file()
    
    def add_rating(self, exchange_name: str, criterion: str, rating: int) -> None:
        """
        Add a rating programmatically (non-interactive).
        
        Args:
            exchange_name: Name of the exchange
            criterion: Rating category
            rating: Rating value (-1 to 4)
        """
        if exchange_name not in self.exchanges:
            raise ValueError(f"Exchange '{exchange_name}' does not exist.")
        
        if criterion not in self.categories:
            raise ValueError(f"Criterion '{criterion}' not in valid categories: {self.categories}")
        
        if not isinstance(rating, int) or rating < -1 or rating > 4:
            raise ValueError(f"Rating must be integer between -1 and 4, got {rating}")
        
        self.exchanges[exchange_name][criterion].append(rating)
        self.exchanges[exchange_name]['_metadata']['total_ratings'] += 1
        
        if self.storage_file:
            self.save_to_file()
    
    def get_rating(self, criterion: str) -> int:
        """Get a rating from the user for a specific criterion (interactive)."""
        print(f"\nRate {criterion.capitalize()}:")
        print("=" * 50)
        
        for rating, description in self.RATING_DESCRIPTIONS.items():
            print(f" {rating:2d}: {description}")
        
        print("=" * 50)
        
        while True:
            try:
                rating = int(input(f"Enter your rating for {criterion.capitalize()} (-1 to 4): "))
                if -1 <= rating <= 4:
                    return rating
                else:
                    print("Please enter a rating between -1 and 4.")
            except ValueError:
                print("Invalid input. Please enter a number between -1 and 4.")
            except KeyboardInterrupt:
                print("\nRating cancelled.")
                sys.exit(0)
    
    def rate_exchange(self, name: str) -> None:
        """Rate an exchange based on Leveson Software Assessment Scale (interactive)."""
        if name not in self.exchanges:
            raise ValueError(f"Exchange '{name}' does not exist.")
        
        print(f"\nRating '{name}' using Leveson-Based Trade Assessment Scale")
        print("=" * 60)
        
        for criterion in self.categories:
            rating = self.get_rating(criterion)
            self.exchanges[name][criterion].append(rating)
            self.exchanges[name]['_metadata']['total_ratings'] += 1
        
        if self.storage_file:
            self.save_to_file()
        
        print(f"\nRating completed for '{name}'!")
    
    def view_ratings(self, name: str) -> Dict[str, Optional[float]]:
        """View the average ratings for a specific exchange."""
        if name not in self.exchanges:
            raise ValueError(f"Exchange '{name}' does not exist.")
        
        ratings_summary = {}
        
        for criterion in self.categories:
            ratings = self.exchanges[name][criterion]
            if ratings:
                avg_rating = sum(ratings) / len(ratings)
                ratings_summary[criterion] = round(avg_rating, 2)
            else:
                ratings_summary[criterion] = None
        
        return ratings_summary
    
    def get_all_exchanges(self) -> List[str]:
        """Return a list of all exchanges."""
        return list(self.exchanges.keys())
    
    def generate_report(self) -> Dict:
        """Generate a comprehensive system report."""
        total_exchanges = len(self.exchanges)
        
        if total_exchanges == 0:
            return {
                'total_exchanges': 0,
                'system_average': None,
                'top_performers': [],
                'bottom_performers': [],
                'category_averages': {}
            }
        
        # Calculate system-wide averages
        all_ratings = []
        category_totals = {cat: [] for cat in self.categories}
        
        exchange_averages = {}
        
        for exchange_name, exchange_data in self.exchanges.items():
            exchange_ratings = []
            
            for category in self.categories:
                ratings = exchange_data[category]
                if ratings:
                    avg = sum(ratings) / len(ratings)
                    exchange_ratings.append(avg)
                    category_totals[category].extend(ratings)
                    all_ratings.extend(ratings)
            
            if exchange_ratings:
                exchange_averages[exchange_name] = sum(exchange_ratings) / len(exchange_ratings)
        
        # System average
        system_average = sum(all_ratings) / len(all_ratings) if all_ratings else None
        
        # Category averages
        category_averages = {}
        for category, ratings in category_totals.items():
            if ratings:
                category_averages[category] = sum(ratings) / len(ratings)
            else:
                category_averages[category] = None
        
        # Top and bottom performers
        sorted_exchanges = sorted(exchange_averages.items(), key=lambda x: x[1], reverse=True)
        top_performers = sorted_exchanges[:5]  # Top 5
        bottom_performers = sorted_exchanges[-5:]  # Bottom 5
        
        return {
            'total_exchanges': total_exchanges,
            'total_ratings': len(all_ratings),
            'system_average': round(system_average, 2) if system_average else None,
            'top_performers': top_performers,
            'bottom_performers': bottom_performers,
            'category_averages': {k: round(v, 2) if v else None for k, v in category_averages.items()},
            'generated_at': datetime.now().isoformat()
        }
    
    def save_to_file(self) -> None:
        """Save exchanges to JSON file."""
        if not self.storage_file:
            return
        
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.exchanges, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save to {self.storage_file}: {e}")
    
    def load_from_file(self) -> None:
        """Load exchanges from JSON file."""
        if not self.storage_file or not os.path.exists(self.storage_file):
            return
        
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Validate loaded data structure
                for exchange_name, exchange_data in data.items():
                    if not isinstance(exchange_data, dict):
                        continue
                    # Ensure all categories exist
                    for category in self.categories:
                        if category not in exchange_data:
                            exchange_data[category] = []
                    # Ensure metadata exists
                    if '_metadata' not in exchange_data:
                        exchange_data['_metadata'] = {
                            'created': datetime.now().isoformat(),
                            'total_ratings': sum(len(ratings) for cat, ratings in exchange_data.items() if cat != '_metadata')
                        }
                
                self.exchanges = data
        except Exception as e:
            print(f"Warning: Could not load from {self.storage_file}: {e}")
    
    def export_to_csv(self, filename: str) -> None:
        """Export ratings to CSV format."""
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['exchange', 'category', 'rating', 'timestamp']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for exchange_name, exchange_data in self.exchanges.items():
                for category in self.categories:
                    for rating in exchange_data[category]:
                        writer.writerow({
                            'exchange': exchange_name,
                            'category': category,
                            'rating': rating,
                            'timestamp': datetime.now().isoformat()
                        })

def main():
    """Command-line interface for LBTAS."""
    parser = argparse.ArgumentParser(
        description="Leveson-Based Trade Assessment Scale (LBTAS)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  lbtas rate --exchange "MyService"
  lbtas add --exchange "MyService" --criterion reliability --rating 3
  lbtas view --exchange "MyService"
  lbtas report
  lbtas export --format csv --output ratings.csv
        """
    )
    
    parser.add_argument('--version', action='version', version=f'LBTAS {__version__}')
    parser.add_argument('--storage', default='lbtas_ratings.json', 
                       help='Storage file for ratings (default: lbtas_ratings.json)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Rate command (interactive)
    rate_parser = subparsers.add_parser('rate', help='Rate an exchange interactively')
    rate_parser.add_argument('--exchange', required=True, help='Exchange name to rate')
    
    # Add command (programmatic)
    add_parser = subparsers.add_parser('add', help='Add a rating programmatically')
    add_parser.add_argument('--exchange', required=True, help='Exchange name')
    add_parser.add_argument('--criterion', required=True, help='Rating criterion')
    add_parser.add_argument('--rating', type=int, required=True, help='Rating value (-1 to 4)')
    
    # View command
    view_parser = subparsers.add_parser('view', help='View ratings for an exchange')
    view_parser.add_argument('--exchange', required=True, help='Exchange name to view')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all exchanges')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate system report')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export ratings')
    export_parser.add_argument('--format', choices=['json', 'csv'], default='json', help='Export format')
    export_parser.add_argument('--output', required=True, help='Output filename')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize rating system
    rating_system = LevesonRatingSystem(storage_file=args.storage)
    
    try:
        if args.command == 'rate':
            if args.exchange not in rating_system.get_all_exchanges():
                rating_system.add_exchange(args.exchange)
            rating_system.rate_exchange(args.exchange)
            
        elif args.command == 'add':
            if args.exchange not in rating_system.get_all_exchanges():
                rating_system.add_exchange(args.exchange)
            rating_system.add_rating(args.exchange, args.criterion, args.rating)
            print(f"Added rating {args.rating} for {args.criterion} to {args.exchange}")
            
        elif args.command == 'view':
            ratings = rating_system.view_ratings(args.exchange)
            print(f"\nRatings for '{args.exchange}':")
            print("=" * 40)
            for criterion, rating in ratings.items():
                if rating is not None:
                    print(f"{criterion.capitalize():12}: {rating:4.2f}")
                else:
                    print(f"{criterion.capitalize():12}: No ratings")
                    
        elif args.command == 'list':
            exchanges = rating_system.get_all_exchanges()
            if exchanges:
                print("Registered exchanges:")
                for exchange in exchanges:
                    ratings = rating_system.view_ratings(exchange)
                    avg = sum(r for r in ratings.values() if r is not None)
                    count = sum(1 for r in ratings.values() if r is not None)
                    overall = avg / count if count > 0 else None
                    if overall:
                        print(f"  {exchange} (avg: {overall:.2f})")
                    else:
                        print(f"  {exchange} (no ratings)")
            else:
                print("No exchanges registered.")
                
        elif args.command == 'report':
            report = rating_system.generate_report()
            print("\nLBTAS System Report")
            print("=" * 50)
            print(f"Total exchanges: {report['total_exchanges']}")
            print(f"Total ratings: {report['total_ratings']}")
            if report['system_average']:
                print(f"System average: {report['system_average']}")
            
            if report['category_averages']:
                print("\nCategory Averages:")
                for category, avg in report['category_averages'].items():
                    if avg:
                        print(f"  {category.capitalize():12}: {avg}")
            
            if report['top_performers']:
                print("\nTop Performers:")
                for exchange, avg in report['top_performers']:
                    print(f"  {exchange}: {avg:.2f}")
                    
        elif args.command == 'export':
            if args.format == 'json':
                with open(args.output, 'w') as f:
                    json.dump(rating_system.exchanges, f, indent=2)
            elif args.format == 'csv':
                rating_system.export_to_csv(args.output)
            print(f"Exported to {args.output}")
            
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

# Example usage when run as script
if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Interactive demo mode
        print("LBTAS Interactive Demo")
        print("=" * 50)
        print("Welcome to the Leveson-Based Trade Assessment Scale!")
        print("This demo will walk you through rating a service.\n")
        
        rating_system = LevesonRatingSystem()
        
        try:
            # Demo exchange
            demo_exchange = "DemoService"
            print(f"Creating demo exchange: '{demo_exchange}'")
            rating_system.add_exchange(demo_exchange)
            
            print("\nYou can now rate this service on four criteria:")
            print("- Reliability: How dependable and consistent is it?")
            print("- Usability: How easy and pleasant is it to use?") 
            print("- Performance: How fast and efficient is it?")
            print("- Support: How helpful is customer service?")
            
            print("\nWould you like to rate this demo service? (y/n): ", end="")
            if input().lower().startswith('y'):
                rating_system.rate_exchange(demo_exchange)
                
                # Show results
                ratings = rating_system.view_ratings(demo_exchange)
                print(f"\nYour ratings for '{demo_exchange}':")
                print("-" * 30)
                for criterion, rating in ratings.items():
                    if rating is not None:
                        description = ""
                        if rating >= 4:
                            description = " (Delight!)"
                        elif rating >= 3:
                            description = " (Excellent)"
                        elif rating >= 2:
                            description = " (Good)"
                        elif rating >= 1:
                            description = " (Acceptable)"
                        elif rating >= 0:
                            description = " (Minimal)"
                        else:
                            description = " (Problematic)"
                        
                        print(f"{criterion.capitalize():12}: {rating:4.1f}{description}")
                
                avg_rating = sum(r for r in ratings.values() if r is not None) / len([r for r in ratings.values() if r is not None])
                print(f"\nOverall Average: {avg_rating:.2f}")
            else:
                print("Demo completed. Try 'python lbtas.py --help' for CLI options.")
                
        except KeyboardInterrupt:
            print("\nDemo cancelled. Goodbye!")
        except Exception as e:
            print(f"Demo error: {e}")
    else:
        # Use CLI interface
        main()
