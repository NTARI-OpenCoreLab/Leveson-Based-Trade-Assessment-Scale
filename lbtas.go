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

package main

import (
	"bufio"
	"encoding/csv"
	"encoding/json"
	"fmt"
	"os"
	"sort"
	"strconv"
	"strings"
	"time"
)

const (
	Version = "1.0.0"
	Author  = "Network Theory Applied Research Institute"
	License = "AGPL-3.0"
)

var defaultCategories = []string{"reliability", "usability", "performance", "support"}

var ratingDescriptions = map[int]string{
	-1: "No Trust - User was harmed, exploited, or received a product or service with no discipline or malicious intent.",
	0:  "Cynical Satisfaction - Interaction fulfills a basic promise requiring little to no discipline toward user satisfaction.",
	1:  "Basic Promise - Interaction meets all articulated user demands, no more.",
	2:  "Basic Satisfaction - Interaction meets socially acceptable standards exceeding articulated user demands.",
	3:  "No Negative Consequences - Interaction designed to prevent loss, exceed basic quality.",
	4:  "Delight - Interaction anticipates the evolution of user practices and concerns post-transaction.",
}

type Metadata struct {
	Created      string `json:"created"`
	TotalRatings int    `json:"total_ratings"`
}

type ExchangeData struct {
	Reliability []int    `json:"reliability"`
	Usability   []int    `json:"usability"`
	Performance []int    `json:"performance"`
	Support     []int    `json:"support"`
	Metadata    Metadata `json:"_metadata"`
}

type StorageData map[string]ExchangeData

type RatingSummary map[string]*float64

type SystemReport struct {
	TotalExchanges   int                    `json:"total_exchanges"`
	TotalRatings     int                    `json:"total_ratings"`
	SystemAverage    *float64               `json:"system_average"`
	CategoryAverages map[string]*float64    `json:"category_averages"`
	TopPerformers    []ExchangePerformance  `json:"top_performers"`
	BottomPerformers []ExchangePerformance  `json:"bottom_performers"`
}

type ExchangePerformance struct {
	Name    string
	Average float64
}

type LevesonRatingSystem struct {
	categories  []string
	storagePath string
	exchanges   StorageData
}

func NewLevesonRatingSystem(storagePath string, categories []string) *LevesonRatingSystem {
	if len(categories) == 0 {
		categories = make([]string, len(defaultCategories))
		copy(categories, defaultCategories)
	}

	lrs := &LevesonRatingSystem{
		categories:  categories,
		storagePath: storagePath,
		exchanges:   make(StorageData),
	}

	if storagePath != "" {
		lrs.loadFromFile()
	}

	return lrs
}

func (lrs *LevesonRatingSystem) loadFromFile() error {
	data, err := os.ReadFile(lrs.storagePath)
	if err != nil {
		if os.IsNotExist(err) {
			return nil
		}
		return err
	}

	return json.Unmarshal(data, &lrs.exchanges)
}

func (lrs *LevesonRatingSystem) saveToFile() error {
	if lrs.storagePath == "" {
		return nil
	}

	data, err := json.MarshalIndent(lrs.exchanges, "", "  ")
	if err != nil {
		return err
	}

	return os.WriteFile(lrs.storagePath, data, 0644)
}

func (lrs *LevesonRatingSystem) AddExchange(name string) error {
	if _, exists := lrs.exchanges[name]; exists {
		return fmt.Errorf("exchange '%s' already exists", name)
	}

	lrs.exchanges[name] = ExchangeData{
		Reliability: []int{},
		Usability:   []int{},
		Performance: []int{},
		Support:     []int{},
		Metadata: Metadata{
			Created:      time.Now().Format(time.RFC3339),
			TotalRatings: 0,
		},
	}

	return lrs.saveToFile()
}

func (lrs *LevesonRatingSystem) AddRating(exchangeName, criterion string, rating int) error {
	exchange, exists := lrs.exchanges[exchangeName]
	if !exists {
		return fmt.Errorf("exchange '%s' does not exist", exchangeName)
	}

	if !contains(lrs.categories, criterion) {
		return fmt.Errorf("criterion '%s' not in valid categories: %v", criterion, lrs.categories)
	}

	if rating < -1 || rating > 4 {
		return fmt.Errorf("rating must be between -1 and 4, got %d", rating)
	}

	switch criterion {
	case "reliability":
		exchange.Reliability = append(exchange.Reliability, rating)
	case "usability":
		exchange.Usability = append(exchange.Usability, rating)
	case "performance":
		exchange.Performance = append(exchange.Performance, rating)
	case "support":
		exchange.Support = append(exchange.Support, rating)
	}

	exchange.Metadata.TotalRatings++
	lrs.exchanges[exchangeName] = exchange

	return lrs.saveToFile()
}

func (lrs *LevesonRatingSystem) GetRating(criterion string) (int, error) {
	reader := bufio.NewReader(os.Stdin)

	fmt.Printf("\nRate %s:\n", strings.Title(criterion))
	fmt.Println(strings.Repeat("=", 50))

	for rating := 4; rating >= -1; rating-- {
		fmt.Printf(" %2d: %s\n", rating, ratingDescriptions[rating])
	}

	fmt.Println(strings.Repeat("=", 50))

	for {
		fmt.Printf("Enter your rating for %s (-1 to 4): ", strings.Title(criterion))
		input, _ := reader.ReadString('\n')
		input = strings.TrimSpace(input)

		rating, err := strconv.Atoi(input)
		if err == nil && rating >= -1 && rating <= 4 {
			return rating, nil
		}

		fmt.Println("Please enter a rating between -1 and 4.")
	}
}

func (lrs *LevesonRatingSystem) RateExchange(name string) error {
	if _, exists := lrs.exchanges[name]; !exists {
		return fmt.Errorf("exchange '%s' does not exist", name)
	}

	fmt.Printf("\nRating '%s' using Leveson-Based Trade Assessment Scale\n", name)
	fmt.Println(strings.Repeat("=", 60))

	for _, criterion := range lrs.categories {
		rating, err := lrs.GetRating(criterion)
		if err != nil {
			return err
		}

		if err := lrs.AddRating(name, criterion, rating); err != nil {
			return err
		}
	}

	fmt.Printf("\nRating completed for '%s'!\n", name)
	return nil
}

func (lrs *LevesonRatingSystem) ViewRatings(name string) (RatingSummary, error) {
	exchange, exists := lrs.exchanges[name]
	if !exists {
		return nil, fmt.Errorf("exchange '%s' does not exist", name)
	}

	summary := make(RatingSummary)

	categoryRatings := map[string][]int{
		"reliability": exchange.Reliability,
		"usability":   exchange.Usability,
		"performance": exchange.Performance,
		"support":     exchange.Support,
	}

	for _, criterion := range lrs.categories {
		ratings := categoryRatings[criterion]
		if len(ratings) > 0 {
			avg := average(ratings)
			summary[criterion] = &avg
		} else {
			summary[criterion] = nil
		}
	}

	return summary, nil
}

func (lrs *LevesonRatingSystem) GetAllExchanges() []string {
	exchanges := make([]string, 0, len(lrs.exchanges))
	for name := range lrs.exchanges {
		exchanges = append(exchanges, name)
	}
	sort.Strings(exchanges)
	return exchanges
}

func (lrs *LevesonRatingSystem) GenerateReport() SystemReport {
	totalExchanges := len(lrs.exchanges)

	if totalExchanges == 0 {
		return SystemReport{
			TotalExchanges:   0,
			TotalRatings:     0,
			SystemAverage:    nil,
			CategoryAverages: make(map[string]*float64),
			TopPerformers:    []ExchangePerformance{},
			BottomPerformers: []ExchangePerformance{},
		}
	}

	var allRatings []int
	categoryTotals := make(map[string][]int)
	for _, category := range lrs.categories {
		categoryTotals[category] = []int{}
	}

	exchangeAverages := make(map[string]float64)

	for exchangeName, exchangeData := range lrs.exchanges {
		var exchangeRatings []float64

		categoryRatings := map[string][]int{
			"reliability": exchangeData.Reliability,
			"usability":   exchangeData.Usability,
			"performance": exchangeData.Performance,
			"support":     exchangeData.Support,
		}

		for _, category := range lrs.categories {
			ratings := categoryRatings[category]
			if len(ratings) > 0 {
				avg := average(ratings)
				exchangeRatings = append(exchangeRatings, avg)
				categoryTotals[category] = append(categoryTotals[category], ratings...)
				allRatings = append(allRatings, ratings...)
			}
		}

		if len(exchangeRatings) > 0 {
			exchangeAverages[exchangeName] = averageFloat(exchangeRatings)
		}
	}

	var systemAverage *float64
	if len(allRatings) > 0 {
		avg := average(allRatings)
		systemAverage = &avg
	}

	categoryAverages := make(map[string]*float64)
	for category, ratings := range categoryTotals {
		if len(ratings) > 0 {
			avg := average(ratings)
			categoryAverages[category] = &avg
		} else {
			categoryAverages[category] = nil
		}
	}

	performances := make([]ExchangePerformance, 0, len(exchangeAverages))
	for name, avg := range exchangeAverages {
		performances = append(performances, ExchangePerformance{Name: name, Average: avg})
	}

	sort.Slice(performances, func(i, j int) bool {
		return performances[i].Average > performances[j].Average
	})

	topPerformers := performances
	if len(topPerformers) > 5 {
		topPerformers = topPerformers[:5]
	}

	bottomPerformers := make([]ExchangePerformance, 0)
	if len(performances) > 0 {
		start := len(performances) - 5
		if start < 0 {
			start = 0
		}
		bottomPerformers = performances[start:]
		for i, j := 0, len(bottomPerformers)-1; i < j; i, j = i+1, j-1 {
			bottomPerformers[i], bottomPerformers[j] = bottomPerformers[j], bottomPerformers[i]
		}
	}

	return SystemReport{
		TotalExchanges:   totalExchanges,
		TotalRatings:     len(allRatings),
		SystemAverage:    systemAverage,
		CategoryAverages: categoryAverages,
		TopPerformers:    topPerformers,
		BottomPerformers: bottomPerformers,
	}
}

func (lrs *LevesonRatingSystem) ExportToJSON(outputPath string) error {
	data, err := json.MarshalIndent(lrs.exchanges, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(outputPath, data, 0644)
}

func (lrs *LevesonRatingSystem) ExportToCSV(outputPath string) error {
	file, err := os.Create(outputPath)
	if err != nil {
		return err
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	writer.Write([]string{"exchange", "category", "rating", "index"})

	for exchangeName, exchangeData := range lrs.exchanges {
		categoryRatings := map[string][]int{
			"reliability": exchangeData.Reliability,
			"usability":   exchangeData.Usability,
			"performance": exchangeData.Performance,
			"support":     exchangeData.Support,
		}

		for _, category := range lrs.categories {
			ratings := categoryRatings[category]
			for i, rating := range ratings {
				writer.Write([]string{
					exchangeName,
					category,
					strconv.Itoa(rating),
					strconv.Itoa(i + 1),
				})
			}
		}
	}

	return nil
}

func average(numbers []int) float64 {
	if len(numbers) == 0 {
		return 0
	}
	sum := 0
	for _, n := range numbers {
		sum += n
	}
	return float64(sum) / float64(len(numbers))
}

func averageFloat(numbers []float64) float64 {
	if len(numbers) == 0 {
		return 0
	}
	sum := 0.0
	for _, n := range numbers {
		sum += n
	}
	return sum / float64(len(numbers))
}

func contains(slice []string, item string) bool {
	for _, s := range slice {
		if s == item {
			return true
		}
	}
	return false
}

func main() {
	if len(os.Args) < 2 {
		fmt.Println("LBTAS - Leveson-Based Trade Assessment Scale")
		fmt.Println("\nUsage:")
		fmt.Println("  lbtas rate <exchange>")
		fmt.Println("  lbtas add <exchange> <criterion> <rating>")
		fmt.Println("  lbtas view <exchange>")
		fmt.Println("  lbtas list")
		fmt.Println("  lbtas report")
		fmt.Println("  lbtas export <format> <output>")
		return
	}

	command := os.Args[1]
	storage := "lbtas_ratings.json"
	system := NewLevesonRatingSystem(storage, nil)

	switch command {
	case "rate":
		if len(os.Args) < 3 {
			fmt.Println("Error: Exchange name required")
			os.Exit(1)
		}
		exchange := os.Args[2]
		if !contains(system.GetAllExchanges(), exchange) {
			if err := system.AddExchange(exchange); err != nil {
				fmt.Printf("Error: %v\n", err)
				os.Exit(1)
			}
		}
		if err := system.RateExchange(exchange); err != nil {
			fmt.Printf("Error: %v\n", err)
			os.Exit(1)
		}

	case "add":
		if len(os.Args) < 5 {
			fmt.Println("Error: exchange, criterion, and rating required")
			os.Exit(1)
		}
		exchange := os.Args[2]
		criterion := os.Args[3]
		rating, err := strconv.Atoi(os.Args[4])
		if err != nil {
			fmt.Printf("Error: invalid rating: %v\n", err)
			os.Exit(1)
		}

		if !contains(system.GetAllExchanges(), exchange) {
			if err := system.AddExchange(exchange); err != nil {
				fmt.Printf("Error: %v\n", err)
				os.Exit(1)
			}
		}

		if err := system.AddRating(exchange, criterion, rating); err != nil {
			fmt.Printf("Error: %v\n", err)
			os.Exit(1)
		}
		fmt.Printf("Added rating %d for %s to %s\n", rating, criterion, exchange)

	case "view":
		if len(os.Args) < 3 {
			fmt.Println("Error: Exchange name required")
			os.Exit(1)
		}
		exchange := os.Args[2]
		ratings, err := system.ViewRatings(exchange)
		if err != nil {
			fmt.Printf("Error: %v\n", err)
			os.Exit(1)
		}

		fmt.Printf("\nRatings for '%s':\n", exchange)
		fmt.Println(strings.Repeat("=", 40))
		for _, criterion := range system.categories {
			if rating := ratings[criterion]; rating != nil {
				fmt.Printf("%-12s: %4.2f\n", strings.Title(criterion), *rating)
			} else {
				fmt.Printf("%-12s: No ratings\n", strings.Title(criterion))
			}
		}

	case "list":
		exchanges := system.GetAllExchanges()
		if len(exchanges) == 0 {
			fmt.Println("No exchanges registered.")
		} else {
			fmt.Println("Registered exchanges:")
			for _, exchange := range exchanges {
				ratings, _ := system.ViewRatings(exchange)
				var sum float64
				var count int
				for _, rating := range ratings {
					if rating != nil {
						sum += *rating
						count++
					}
				}
				if count > 0 {
					fmt.Printf("  %s (avg: %.2f)\n", exchange, sum/float64(count))
				} else {
					fmt.Printf("  %s (no ratings)\n", exchange)
				}
			}
		}

	case "report":
		report := system.GenerateReport()
		fmt.Println("\nLBTAS System Report")
		fmt.Println(strings.Repeat("=", 50))
		fmt.Printf("Total exchanges: %d\n", report.TotalExchanges)
		fmt.Printf("Total ratings: %d\n", report.TotalRatings)
		if report.SystemAverage != nil {
			fmt.Printf("System average: %.2f\n", *report.SystemAverage)
		}

		if len(report.CategoryAverages) > 0 {
			fmt.Println("\nCategory Averages:")
			for _, category := range system.categories {
				if avg := report.CategoryAverages[category]; avg != nil {
					fmt.Printf("  %-12s: %.2f\n", strings.Title(category), *avg)
				}
			}
		}

		if len(report.TopPerformers) > 0 {
			fmt.Println("\nTop Performers:")
			for _, perf := range report.TopPerformers {
				fmt.Printf("  %s: %.2f\n", perf.Name, perf.Average)
			}
		}

	case "export":
		if len(os.Args) < 4 {
			fmt.Println("Error: format and output path required")
			os.Exit(1)
		}
		format := os.Args[2]
		output := os.Args[3]

		var err error
		switch format {
		case "json":
			err = system.ExportToJSON(output)
		case "csv":
			err = system.ExportToCSV(output)
		default:
			fmt.Println("Error: format must be json or csv")
			os.Exit(1)
		}

		if err != nil {
			fmt.Printf("Error: %v\n", err)
			os.Exit(1)
		}
		fmt.Printf("Exported to %s\n", output)

	default:
		fmt.Printf("Unknown command: %s\n", command)
		os.Exit(1)
	}
}
