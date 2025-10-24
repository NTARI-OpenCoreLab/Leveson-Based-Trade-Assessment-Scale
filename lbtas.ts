/**
 * Leveson-Based Trade Assessment Scale (LBTAS)
 * 
 * A rating system for digital commerce based on Nancy Leveson's
 * aircraft software assessment methodology.
 * 
 * Copyright (C) 2024 Network Theory Applied Research Institute
 * Licensed under GNU Affero General Public License v3.0
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 */

import * as fs from 'fs';
import * as readline from 'readline';

const VERSION = '1.0.0';
const AUTHOR = 'Network Theory Applied Research Institute';
const LICENSE = 'AGPL-3.0';

interface ExchangeData {
  [category: string]: number[];
  _metadata: {
    created: string;
    total_ratings: number;
  };
}

interface StorageData {
  [exchange: string]: ExchangeData;
}

interface RatingSummary {
  [category: string]: number | null;
}

interface SystemReport {
  total_exchanges: number;
  total_ratings: number;
  system_average: number | null;
  category_averages: { [key: string]: number | null };
  top_performers: Array<[string, number]>;
  bottom_performers: Array<[string, number]>;
}

class LevesonRatingSystem {
  private readonly DEFAULT_CATEGORIES = ['reliability', 'usability', 'performance', 'support'];
  
  private readonly RATING_DESCRIPTIONS: { [key: number]: string } = {
    '-1': 'No Trust - User was harmed, exploited, or received a product or service with no discipline or malicious intent.',
    '0': 'Cynical Satisfaction - Interaction fulfills a basic promise requiring little to no discipline toward user satisfaction.',
    '1': 'Basic Promise - Interaction meets all articulated user demands, no more.',
    '2': 'Basic Satisfaction - Interaction meets socially acceptable standards exceeding articulated user demands.',
    '3': 'No Negative Consequences - Interaction designed to prevent loss, exceed basic quality.',
    '4': 'Delight - Interaction anticipates the evolution of user practices and concerns post-transaction.'
  };

  private categories: string[];
  private storagePath: string | null;
  private exchanges: StorageData;

  constructor(storagePath: string | null = null, categories: string[] | null = null) {
    this.categories = categories || this.DEFAULT_CATEGORIES.slice();
    this.storagePath = storagePath;
    this.exchanges = {};

    if (this.storagePath) {
      this.loadFromFile();
    }
  }

  private loadFromFile(): void {
    if (!this.storagePath) return;
    
    try {
      if (fs.existsSync(this.storagePath)) {
        const data = fs.readFileSync(this.storagePath, 'utf8');
        this.exchanges = JSON.parse(data);
      }
    } catch (error) {
      console.error(`Error loading from file: ${error}`);
    }
  }

  private saveToFile(): void {
    if (!this.storagePath) return;
    
    try {
      fs.writeFileSync(this.storagePath, JSON.stringify(this.exchanges, null, 2));
    } catch (error) {
      console.error(`Error saving to file: ${error}`);
    }
  }

  addExchange(name: string): void {
    if (this.exchanges[name]) {
      throw new Error(`Exchange '${name}' already exists.`);
    }

    const exchangeData: ExchangeData = {
      _metadata: {
        created: new Date().toISOString(),
        total_ratings: 0
      }
    };

    for (const category of this.categories) {
      exchangeData[category] = [];
    }

    this.exchanges[name] = exchangeData;
    this.saveToFile();
  }

  addRating(exchangeName: string, criterion: string, rating: number): void {
    if (!this.exchanges[exchangeName]) {
      throw new Error(`Exchange '${exchangeName}' does not exist.`);
    }

    if (!this.categories.includes(criterion)) {
      throw new Error(`Criterion '${criterion}' not in valid categories: ${this.categories.join(', ')}`);
    }

    if (!Number.isInteger(rating) || rating < -1 || rating > 4) {
      throw new Error(`Rating must be integer between -1 and 4, got ${rating}`);
    }

    this.exchanges[exchangeName][criterion].push(rating);
    this.exchanges[exchangeName]._metadata.total_ratings++;
    this.saveToFile();
  }

  async getRating(criterion: string): Promise<number> {
    console.log(`\nRate ${criterion.charAt(0).toUpperCase() + criterion.slice(1)}:`);
    console.log('='.repeat(50));
    
    for (const [rating, description] of Object.entries(this.RATING_DESCRIPTIONS)) {
      console.log(`${rating.padStart(2)}: ${description}`);
    }
    
    console.log('='.repeat(50));

    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });

    return new Promise((resolve) => {
      const askRating = () => {
        rl.question(`Enter your rating for ${criterion.charAt(0).toUpperCase() + criterion.slice(1)} (-1 to 4): `, (answer) => {
          const rating = parseInt(answer);
          if (!isNaN(rating) && rating >= -1 && rating <= 4) {
            rl.close();
            resolve(rating);
          } else {
            console.log('Please enter a rating between -1 and 4.');
            askRating();
          }
        });
      };
      askRating();
    });
  }

  async rateExchange(name: string): Promise<void> {
    if (!this.exchanges[name]) {
      throw new Error(`Exchange '${name}' does not exist.`);
    }

    console.log(`\nRating '${name}' using Leveson-Based Trade Assessment Scale`);
    console.log('='.repeat(60));

    for (const criterion of this.categories) {
      const rating = await this.getRating(criterion);
      this.exchanges[name][criterion].push(rating);
      this.exchanges[name]._metadata.total_ratings++;
    }

    this.saveToFile();
    console.log(`\nRating completed for '${name}'!`);
  }

  viewRatings(name: string): RatingSummary {
    if (!this.exchanges[name]) {
      throw new Error(`Exchange '${name}' does not exist.`);
    }

    const summary: RatingSummary = {};

    for (const criterion of this.categories) {
      const ratings = this.exchanges[name][criterion];
      if (ratings.length > 0) {
        const avg = ratings.reduce((a, b) => a + b, 0) / ratings.length;
        summary[criterion] = Math.round(avg * 100) / 100;
      } else {
        summary[criterion] = null;
      }
    }

    return summary;
  }

  getAllExchanges(): string[] {
    return Object.keys(this.exchanges);
  }

  generateReport(): SystemReport {
    const totalExchanges = Object.keys(this.exchanges).length;

    if (totalExchanges === 0) {
      return {
        total_exchanges: 0,
        total_ratings: 0,
        system_average: null,
        category_averages: {},
        top_performers: [],
        bottom_performers: []
      };
    }

    const allRatings: number[] = [];
    const categoryTotals: { [key: string]: number[] } = {};
    const exchangeAverages: { [key: string]: number } = {};

    for (const category of this.categories) {
      categoryTotals[category] = [];
    }

    for (const [exchangeName, exchangeData] of Object.entries(this.exchanges)) {
      const exchangeRatings: number[] = [];

      for (const category of this.categories) {
        const ratings = exchangeData[category];
        if (ratings.length > 0) {
          const avg = ratings.reduce((a, b) => a + b, 0) / ratings.length;
          exchangeRatings.push(avg);
          categoryTotals[category].push(avg);
          allRatings.push(...ratings);
        }
      }

      if (exchangeRatings.length > 0) {
        exchangeAverages[exchangeName] = 
          exchangeRatings.reduce((a, b) => a + b, 0) / exchangeRatings.length;
      }
    }

    const systemAverage = allRatings.length > 0
      ? allRatings.reduce((a, b) => a + b, 0) / allRatings.length
      : null;

    const categoryAverages: { [key: string]: number | null } = {};
    for (const [category, ratings] of Object.entries(categoryTotals)) {
      categoryAverages[category] = ratings.length > 0
        ? ratings.reduce((a, b) => a + b, 0) / ratings.length
        : null;
    }

    const sortedExchanges = Object.entries(exchangeAverages)
      .sort((a, b) => b[1] - a[1]);

    const topPerformers = sortedExchanges.slice(0, 5);
    const bottomPerformers = sortedExchanges.slice(-5).reverse();

    return {
      total_exchanges: totalExchanges,
      total_ratings: allRatings.length,
      system_average: systemAverage,
      category_averages: categoryAverages,
      top_performers: topPerformers,
      bottom_performers: bottomPerformers
    };
  }

  exportToJSON(outputPath: string): void {
    fs.writeFileSync(outputPath, JSON.stringify(this.exchanges, null, 2));
  }

  exportToCSV(outputPath: string): void {
    const lines: string[] = ['exchange,category,rating,timestamp'];

    for (const [exchangeName, exchangeData] of Object.entries(this.exchanges)) {
      for (const category of this.categories) {
        const ratings = exchangeData[category];
        for (let i = 0; i < ratings.length; i++) {
          lines.push(`${exchangeName},${category},${ratings[i]},${i + 1}`);
        }
      }
    }

    fs.writeFileSync(outputPath, lines.join('\n'));
  }
}

// CLI interface
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log('LBTAS - Leveson-Based Trade Assessment Scale');
    console.log('\nUsage:');
    console.log('  node lbtas.js rate <exchange>');
    console.log('  node lbtas.js add <exchange> <criterion> <rating>');
    console.log('  node lbtas.js view <exchange>');
    console.log('  node lbtas.js list');
    console.log('  node lbtas.js report');
    console.log('  node lbtas.js export <format> <output>');
    return;
  }

  const command = args[0];
  const storage = 'lbtas_ratings.json';
  const system = new LevesonRatingSystem(storage);

  try {
    switch (command) {
      case 'rate': {
        const exchange = args[1];
        if (!exchange) {
          console.error('Error: Exchange name required');
          return;
        }
        if (!system.getAllExchanges().includes(exchange)) {
          system.addExchange(exchange);
        }
        await system.rateExchange(exchange);
        break;
      }

      case 'add': {
        const [, exchange, criterion, ratingStr] = args;
        if (!exchange || !criterion || !ratingStr) {
          console.error('Error: exchange, criterion, and rating required');
          return;
        }
        const rating = parseInt(ratingStr);
        if (!system.getAllExchanges().includes(exchange)) {
          system.addExchange(exchange);
        }
        system.addRating(exchange, criterion, rating);
        console.log(`Added rating ${rating} for ${criterion} to ${exchange}`);
        break;
      }

      case 'view': {
        const exchange = args[1];
        if (!exchange) {
          console.error('Error: Exchange name required');
          return;
        }
        const ratings = system.viewRatings(exchange);
        console.log(`\nRatings for '${exchange}':`);
        console.log('='.repeat(40));
        for (const [criterion, rating] of Object.entries(ratings)) {
          if (rating !== null) {
            console.log(`${criterion.padEnd(12)}: ${rating.toFixed(2)}`);
          } else {
            console.log(`${criterion.padEnd(12)}: No ratings`);
          }
        }
        break;
      }

      case 'list': {
        const exchanges = system.getAllExchanges();
        if (exchanges.length === 0) {
          console.log('No exchanges registered.');
        } else {
          console.log('Registered exchanges:');
          for (const exchange of exchanges) {
            const ratings = system.viewRatings(exchange);
            const values = Object.values(ratings).filter(r => r !== null) as number[];
            const overall = values.length > 0
              ? values.reduce((a, b) => a + b, 0) / values.length
              : null;
            if (overall !== null) {
              console.log(`  ${exchange} (avg: ${overall.toFixed(2)})`);
            } else {
              console.log(`  ${exchange} (no ratings)`);
            }
          }
        }
        break;
      }

      case 'report': {
        const report = system.generateReport();
        console.log('\nLBTAS System Report');
        console.log('='.repeat(50));
        console.log(`Total exchanges: ${report.total_exchanges}`);
        console.log(`Total ratings: ${report.total_ratings}`);
        if (report.system_average !== null) {
          console.log(`System average: ${report.system_average.toFixed(2)}`);
        }

        if (Object.keys(report.category_averages).length > 0) {
          console.log('\nCategory Averages:');
          for (const [category, avg] of Object.entries(report.category_averages)) {
            if (avg !== null) {
              console.log(`  ${category.padEnd(12)}: ${avg.toFixed(2)}`);
            }
          }
        }

        if (report.top_performers.length > 0) {
          console.log('\nTop Performers:');
          for (const [exchange, avg] of report.top_performers) {
            console.log(`  ${exchange}: ${avg.toFixed(2)}`);
          }
        }
        break;
      }

      case 'export': {
        const format = args[1];
        const output = args[2];
        if (!format || !output) {
          console.error('Error: format and output path required');
          return;
        }
        if (format === 'json') {
          system.exportToJSON(output);
        } else if (format === 'csv') {
          system.exportToCSV(output);
        } else {
          console.error('Error: format must be json or csv');
          return;
        }
        console.log(`Exported to ${output}`);
        break;
      }

      default:
        console.error(`Unknown command: ${command}`);
    }
  } catch (error) {
    console.error(`Error: ${error}`);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

export { LevesonRatingSystem };
