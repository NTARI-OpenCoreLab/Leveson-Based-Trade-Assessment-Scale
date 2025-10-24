// Leveson-Based Trade Assessment Scale (LBTAS)
//
// A rating system for digital commerce based on Nancy Leveson's
// aircraft software assessment methodology.
//
// Copyright (C) 2024 Network Theory Applied Research Institute
// Licensed under GNU Affero General Public License v3.0
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

use std::collections::HashMap;
use std::fs;
use std::io::{self, Write};
use serde::{Deserialize, Serialize};
use chrono::Utc;

const VERSION: &str = "1.0.0";
const AUTHOR: &str = "Network Theory Applied Research Institute";
const LICENSE: &str = "AGPL-3.0";

const DEFAULT_CATEGORIES: &[&str] = &["reliability", "usability", "performance", "support"];

fn rating_descriptions() -> HashMap<i8, &'static str> {
    let mut map = HashMap::new();
    map.insert(-1, "No Trust - User was harmed, exploited, or received a product or service with no discipline or malicious intent.");
    map.insert(0, "Cynical Satisfaction - Interaction fulfills a basic promise requiring little to no discipline toward user satisfaction.");
    map.insert(1, "Basic Promise - Interaction meets all articulated user demands, no more.");
    map.insert(2, "Basic Satisfaction - Interaction meets socially acceptable standards exceeding articulated user demands.");
    map.insert(3, "No Negative Consequences - Interaction designed to prevent loss, exceed basic quality.");
    map.insert(4, "Delight - Interaction anticipates the evolution of user practices and concerns post-transaction.");
    map
}

#[derive(Debug, Serialize, Deserialize, Clone)]
struct Metadata {
    created: String,
    total_ratings: usize,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
struct ExchangeData {
    reliability: Vec<i8>,
    usability: Vec<i8>,
    performance: Vec<i8>,
    support: Vec<i8>,
    #[serde(rename = "_metadata")]
    metadata: Metadata,
}

impl ExchangeData {
    fn new() -> Self {
        ExchangeData {
            reliability: Vec::new(),
            usability: Vec::new(),
            performance: Vec::new(),
            support: Vec::new(),
            metadata: Metadata {
                created: Utc::now().to_rfc3339(),
                total_ratings: 0,
            },
        }
    }

    fn get_category_mut(&mut self, category: &str) -> Option<&mut Vec<i8>> {
        match category {
            "reliability" => Some(&mut self.reliability),
            "usability" => Some(&mut self.usability),
            "performance" => Some(&mut self.performance),
            "support" => Some(&mut self.support),
            _ => None,
        }
    }

    fn get_category(&self, category: &str) -> Option<&Vec<i8>> {
        match category {
            "reliability" => Some(&self.reliability),
            "usability" => Some(&self.usability),
            "performance" => Some(&self.performance),
            "support" => Some(&self.support),
            _ => None,
        }
    }
}

#[derive(Debug, Serialize, Deserialize)]
struct StorageData {
    #[serde(flatten)]
    exchanges: HashMap<String, ExchangeData>,
}

#[derive(Debug)]
struct RatingSummary {
    ratings: HashMap<String, Option<f64>>,
}

#[derive(Debug)]
struct ExchangePerformance {
    name: String,
    average: f64,
}

#[derive(Debug)]
struct SystemReport {
    total_exchanges: usize,
    total_ratings: usize,
    system_average: Option<f64>,
    category_averages: HashMap<String, Option<f64>>,
    top_performers: Vec<ExchangePerformance>,
    bottom_performers: Vec<ExchangePerformance>,
}

struct LevesonRatingSystem {
    categories: Vec<String>,
    storage_path: Option<String>,
    exchanges: HashMap<String, ExchangeData>,
}

impl LevesonRatingSystem {
    fn new(storage_path: Option<String>, categories: Option<Vec<String>>) -> Self {
        let categories = categories.unwrap_or_else(|| {
            DEFAULT_CATEGORIES.iter().map(|s| s.to_string()).collect()
        });

        let mut system = LevesonRatingSystem {
            categories,
            storage_path,
            exchanges: HashMap::new(),
        };

        if system.storage_path.is_some() {
            let _ = system.load_from_file();
        }

        system
    }

    fn load_from_file(&mut self) -> Result<(), Box<dyn std::error::Error>> {
        if let Some(path) = &self.storage_path {
            if std::path::Path::new(path).exists() {
                let data = fs::read_to_string(path)?;
                let storage: StorageData = serde_json::from_str(&data)?;
                self.exchanges = storage.exchanges;
            }
        }
        Ok(())
    }

    fn save_to_file(&self) -> Result<(), Box<dyn std::error::Error>> {
        if let Some(path) = &self.storage_path {
            let storage = StorageData {
                exchanges: self.exchanges.clone(),
            };
            let data = serde_json::to_string_pretty(&storage)?;
            fs::write(path, data)?;
        }
        Ok(())
    }

    fn add_exchange(&mut self, name: &str) -> Result<(), String> {
        if self.exchanges.contains_key(name) {
            return Err(format!("Exchange '{}' already exists", name));
        }

        self.exchanges.insert(name.to_string(), ExchangeData::new());
        self.save_to_file().map_err(|e| e.to_string())?;
        Ok(())
    }

    fn add_rating(&mut self, exchange_name: &str, criterion: &str, rating: i8) -> Result<(), String> {
        let exchange = self.exchanges.get_mut(exchange_name)
            .ok_or_else(|| format!("Exchange '{}' does not exist", exchange_name))?;

        if !self.categories.contains(&criterion.to_string()) {
            return Err(format!("Criterion '{}' not in valid categories: {:?}", criterion, self.categories));
        }

        if rating < -1 || rating > 4 {
            return Err(format!("Rating must be between -1 and 4, got {}", rating));
        }

        if let Some(category) = exchange.get_category_mut(criterion) {
            category.push(rating);
            exchange.metadata.total_ratings += 1;
            self.save_to_file().map_err(|e| e.to_string())?;
            Ok(())
        } else {
            Err(format!("Invalid category: {}", criterion))
        }
    }

    fn get_rating(&self, criterion: &str) -> Result<i8, Box<dyn std::error::Error>> {
        let descriptions = rating_descriptions();

        println!("\nRate {}:", criterion.chars().next().unwrap().to_uppercase().collect::<String>() + &criterion[1..]);
        println!("{}", "=".repeat(50));

        for rating in ((-1)..=4).rev() {
            println!(" {:2}: {}", rating, descriptions.get(&rating).unwrap());
        }

        println!("{}", "=".repeat(50));

        loop {
            print!("Enter your rating for {} (-1 to 4): ", criterion.chars().next().unwrap().to_uppercase().collect::<String>() + &criterion[1..]);
            io::stdout().flush()?;

            let mut input = String::new();
            io::stdin().read_line(&mut input)?;

            if let Ok(rating) = input.trim().parse::<i8>() {
                if rating >= -1 && rating <= 4 {
                    return Ok(rating);
                }
            }

            println!("Please enter a rating between -1 and 4.");
        }
    }

    fn rate_exchange(&mut self, name: &str) -> Result<(), Box<dyn std::error::Error>> {
        if !self.exchanges.contains_key(name) {
            return Err(format!("Exchange '{}' does not exist", name).into());
        }

        println!("\nRating '{}' using Leveson-Based Trade Assessment Scale", name);
        println!("{}", "=".repeat(60));

        for criterion in self.categories.clone() {
            let rating = self.get_rating(&criterion)?;
            self.add_rating(name, &criterion, rating)?;
        }

        println!("\nRating completed for '{}'!", name);
        Ok(())
    }

    fn view_ratings(&self, name: &str) -> Result<RatingSummary, String> {
        let exchange = self.exchanges.get(name)
            .ok_or_else(|| format!("Exchange '{}' does not exist", name))?;

        let mut ratings = HashMap::new();

        for criterion in &self.categories {
            if let Some(category) = exchange.get_category(criterion) {
                if !category.is_empty() {
                    let sum: i32 = category.iter().map(|&x| x as i32).sum();
                    let avg = sum as f64 / category.len() as f64;
                    ratings.insert(criterion.clone(), Some((avg * 100.0).round() / 100.0));
                } else {
                    ratings.insert(criterion.clone(), None);
                }
            }
        }

        Ok(RatingSummary { ratings })
    }

    fn get_all_exchanges(&self) -> Vec<String> {
        let mut exchanges: Vec<String> = self.exchanges.keys().cloned().collect();
        exchanges.sort();
        exchanges
    }

    fn generate_report(&self) -> SystemReport {
        if self.exchanges.is_empty() {
            return SystemReport {
                total_exchanges: 0,
                total_ratings: 0,
                system_average: None,
                category_averages: HashMap::new(),
                top_performers: Vec::new(),
                bottom_performers: Vec::new(),
            };
        }

        let mut all_ratings = Vec::new();
        let mut category_totals: HashMap<String, Vec<i8>> = HashMap::new();
        for category in &self.categories {
            category_totals.insert(category.clone(), Vec::new());
        }

        let mut exchange_averages: HashMap<String, f64> = HashMap::new();

        for (exchange_name, exchange_data) in &self.exchanges {
            let mut exchange_ratings = Vec::new();

            for category in &self.categories {
                if let Some(ratings) = exchange_data.get_category(category) {
                    if !ratings.is_empty() {
                        let sum: i32 = ratings.iter().map(|&x| x as i32).sum();
                        let avg = sum as f64 / ratings.len() as f64;
                        exchange_ratings.push(avg);
                        category_totals.get_mut(category).unwrap().extend(ratings);
                        all_ratings.extend(ratings);
                    }
                }
            }

            if !exchange_ratings.is_empty() {
                let sum: f64 = exchange_ratings.iter().sum();
                exchange_averages.insert(exchange_name.clone(), sum / exchange_ratings.len() as f64);
            }
        }

        let system_average = if !all_ratings.is_empty() {
            let sum: i32 = all_ratings.iter().map(|&x| x as i32).sum();
            Some(sum as f64 / all_ratings.len() as f64)
        } else {
            None
        };

        let mut category_averages = HashMap::new();
        for (category, ratings) in &category_totals {
            if !ratings.is_empty() {
                let sum: i32 = ratings.iter().map(|&x| x as i32).sum();
                category_averages.insert(category.clone(), Some(sum as f64 / ratings.len() as f64));
            } else {
                category_averages.insert(category.clone(), None);
            }
        }

        let mut performances: Vec<ExchangePerformance> = exchange_averages.iter()
            .map(|(name, &average)| ExchangePerformance {
                name: name.clone(),
                average,
            })
            .collect();

        performances.sort_by(|a, b| b.average.partial_cmp(&a.average).unwrap());

        let top_performers = performances.iter().take(5).cloned().map(|p| p).collect();
        let bottom_performers: Vec<ExchangePerformance> = performances.iter()
            .rev()
            .take(5)
            .cloned()
            .collect::<Vec<_>>()
            .into_iter()
            .rev()
            .collect();

        SystemReport {
            total_exchanges: self.exchanges.len(),
            total_ratings: all_ratings.len(),
            system_average,
            category_averages,
            top_performers,
            bottom_performers,
        }
    }

    fn export_to_json(&self, output_path: &str) -> Result<(), Box<dyn std::error::Error>> {
        let storage = StorageData {
            exchanges: self.exchanges.clone(),
        };
        let data = serde_json::to_string_pretty(&storage)?;
        fs::write(output_path, data)?;
        Ok(())
    }

    fn export_to_csv(&self, output_path: &str) -> Result<(), Box<dyn std::error::Error>> {
        let mut wtr = csv::Writer::from_path(output_path)?;
        wtr.write_record(&["exchange", "category", "rating", "index"])?;

        for (exchange_name, exchange_data) in &self.exchanges {
            for category in &self.categories {
                if let Some(ratings) = exchange_data.get_category(category) {
                    for (i, &rating) in ratings.iter().enumerate() {
                        wtr.write_record(&[
                            exchange_name,
                            category,
                            &rating.to_string(),
                            &(i + 1).to_string(),
                        ])?;
                    }
                }
            }
        }

        wtr.flush()?;
        Ok(())
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();

    if args.len() < 2 {
        println!("LBTAS - Leveson-Based Trade Assessment Scale");
        println!("\nUsage:");
        println!("  lbtas rate <exchange>");
        println!("  lbtas add <exchange> <criterion> <rating>");
        println!("  lbtas view <exchange>");
        println!("  lbtas list");
        println!("  lbtas report");
        println!("  lbtas export <format> <output>");
        return;
    }

    let command = &args[1];
    let storage = "lbtas_ratings.json".to_string();
    let mut system = LevesonRatingSystem::new(Some(storage), None);

    match command.as_str() {
        "rate" => {
            if args.len() < 3 {
                eprintln!("Error: Exchange name required");
                std::process::exit(1);
            }
            let exchange = &args[2];
            if !system.get_all_exchanges().contains(exchange) {
                if let Err(e) = system.add_exchange(exchange) {
                    eprintln!("Error: {}", e);
                    std::process::exit(1);
                }
            }
            if let Err(e) = system.rate_exchange(exchange) {
                eprintln!("Error: {}", e);
                std::process::exit(1);
            }
        }

        "add" => {
            if args.len() < 5 {
                eprintln!("Error: exchange, criterion, and rating required");
                std::process::exit(1);
            }
            let exchange = &args[2];
            let criterion = &args[3];
            let rating: i8 = match args[4].parse() {
                Ok(r) => r,
                Err(_) => {
                    eprintln!("Error: invalid rating");
                    std::process::exit(1);
                }
            };

            if !system.get_all_exchanges().contains(exchange) {
                if let Err(e) = system.add_exchange(exchange) {
                    eprintln!("Error: {}", e);
                    std::process::exit(1);
                }
            }

            if let Err(e) = system.add_rating(exchange, criterion, rating) {
                eprintln!("Error: {}", e);
                std::process::exit(1);
            }
            println!("Added rating {} for {} to {}", rating, criterion, exchange);
        }

        "view" => {
            if args.len() < 3 {
                eprintln!("Error: Exchange name required");
                std::process::exit(1);
            }
            let exchange = &args[2];
            match system.view_ratings(exchange) {
                Ok(summary) => {
                    println!("\nRatings for '{}':", exchange);
                    println!("{}", "=".repeat(40));
                    for category in &system.categories {
                        if let Some(rating) = summary.ratings.get(category) {
                            match rating {
                                Some(r) => println!("{:12}: {:4.2}", category, r),
                                None => println!("{:12}: No ratings", category),
                            }
                        }
                    }
                }
                Err(e) => {
                    eprintln!("Error: {}", e);
                    std::process::exit(1);
                }
            }
        }

        "list" => {
            let exchanges = system.get_all_exchanges();
            if exchanges.is_empty() {
                println!("No exchanges registered.");
            } else {
                println!("Registered exchanges:");
                for exchange in exchanges {
                    if let Ok(summary) = system.view_ratings(&exchange) {
                        let values: Vec<f64> = summary.ratings.values()
                            .filter_map(|&r| r)
                            .collect();
                        if !values.is_empty() {
                            let avg = values.iter().sum::<f64>() / values.len() as f64;
                            println!("  {} (avg: {:.2})", exchange, avg);
                        } else {
                            println!("  {} (no ratings)", exchange);
                        }
                    }
                }
            }
        }

        "report" => {
            let report = system.generate_report();
            println!("\nLBTAS System Report");
            println!("{}", "=".repeat(50));
            println!("Total exchanges: {}", report.total_exchanges);
            println!("Total ratings: {}", report.total_ratings);
            if let Some(avg) = report.system_average {
                println!("System average: {:.2}", avg);
            }

            if !report.category_averages.is_empty() {
                println!("\nCategory Averages:");
                for category in &system.categories {
                    if let Some(avg) = report.category_averages.get(category) {
                        if let Some(a) = avg {
                            println!("  {:12}: {:.2}", category, a);
                        }
                    }
                }
            }

            if !report.top_performers.is_empty() {
                println!("\nTop Performers:");
                for perf in &report.top_performers {
                    println!("  {}: {:.2}", perf.name, perf.average);
                }
            }
        }

        "export" => {
            if args.len() < 4 {
                eprintln!("Error: format and output path required");
                std::process::exit(1);
            }
            let format = &args[2];
            let output = &args[3];

            let result = match format.as_str() {
                "json" => system.export_to_json(output),
                "csv" => system.export_to_csv(output),
                _ => {
                    eprintln!("Error: format must be json or csv");
                    std::process::exit(1);
                }
            };

            if let Err(e) = result {
                eprintln!("Error: {}", e);
                std::process::exit(1);
            }
            println!("Exported to {}", output);
        }

        _ => {
            eprintln!("Unknown command: {}", command);
            std::process::exit(1);
        }
    }
}
