"""
Leveson Software Assessment Scale
=================================

This module provides a Leveson Software Assessment Scale for rating software exchanges.
It is designed in compliance with the Digital Public Goods Standard.
This software is open-source and is licensed under the MIT License.

Author: Your Name
License: MIT License
"""

class LevesonRatingSystem:
    def __init__(self):
        self.exchanges = {}

    def add_exchange(self, name):
        """Add a new exchange to the system."""
        if name not in self.exchanges:
            self.exchanges[name] = {
                'reliability': [],
                'usability': [],
                'performance': [],
                'support': []
            }
        else:
            raise ValueError(f"Exchange '{name}' already exists.")

    def get_rating(self, criterion):
        """Get a rating from the user for a specific criterion."""
        rating_descriptions = {
            -1: "No Trust - User was harmed, exploited, or received a product or service with no discipline or malicious intent.",
            0: "Cynical Satisfaction - Interaction fulfills a basic promise requiring little to no discipline toward user satisfaction.",
            1: "Basic Promise - Interaction meets all articulated user demands, no more.",
            2: "Basic Satisfaction - Interaction meets socially acceptable standards exceeding articulated user demands.",
            3: "No Negative Consequences - Interaction designed to prevent loss, exceed basic quality.",
            4: "Delight - Interaction anticipates the evolution of user practices and concerns post-transaction."
        }

        print(f"Rate {criterion.capitalize()}:")
        for rating, description in rating_descriptions.items():
            print(f" {rating}: {description}")

        while True:
            try:
                rating = int(input(f"Enter your rating for {criterion.capitalize()} (-1 to 4): "))
                if -1 <= rating <= 4:
                    return rating
                else:
                    print("Please enter a rating between -1 and 4.")
            except ValueError:
                print("Invalid input. Please enter a number between -1 and 4.")

    def rate_exchange(self, name):
        """Rate an exchange based on Leveson Software Assessment Scale."""
        if name not in self.exchanges:
            raise ValueError(f"Exchange '{name}' does not exist.")

        print(f"Rating {name} based on Leveson Software Assessment Scale")
        for criterion in self.exchanges[name]:
            rating = self.get_rating(criterion)
            self.exchanges[name][criterion].append(rating)

    def view_ratings(self, name):
        """View the average ratings for a specific exchange."""
        if name not in self.exchanges:
            raise ValueError(f"Exchange '{name}' does not exist.")

        ratings_summary = {}
        for criterion, ratings in self.exchanges[name].items():
            if ratings:
                avg_rating = sum(ratings) / len(ratings)
                ratings_summary[criterion] = round(avg_rating, 2)
            else:
                ratings_summary[criterion] = None
        
        return ratings_summary

    def get_all_exchanges(self):
        """Return a list of all exchanges."""
        return list(self.exchanges.keys())


# Example usage in a larger program:
if __name__ == "__main__":
    rating_system = LevesonRatingSystem()

    # Adding exchanges
    rating_system.add_exchange("ExampleExchange1")
    rating_system.add_exchange("ExampleExchange2")

    # Rating an exchange
    rating_system.rate_exchange("ExampleExchange1")

    # Viewing ratings
    ratings = rating_system.view_ratings("ExampleExchange1")
    print("Ratings summary:", ratings)
