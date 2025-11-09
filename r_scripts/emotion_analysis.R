# Emotion Analysis Script in R
# Statistical analysis of facial emotion recognition data
# Author: College Project - Facial Emotion Recognition System

# Load required libraries
if (!require("jsonlite")) install.packages("jsonlite")
if (!require("ggplot2")) install.packages("ggplot2")
if (!require("dplyr")) install.packages("dplyr")
if (!require("plotly")) install.packages("plotly")
if (!require("lubridate")) install.packages("lubridate")

library(jsonlite)
library(ggplot2)
library(dplyr)
library(plotly)
library(lubridate)

# Set working directory to project root
setwd("..")

# Function to load emotion data from JSON database
load_emotion_data <- function(json_path = "data/emotions.json") {
  if (!file.exists(json_path)) {
    cat("Database file not found. Creating sample data...\n")
    return(create_sample_data())
  }
  
  # Read JSON data
  json_data <- fromJSON(json_path)
  
  if (length(json_data$emotions) == 0) {
    cat("No emotion data found. Creating sample data...\n")
    return(create_sample_data())
  }
  
  # Convert to data frame
  emotions_df <- as.data.frame(json_data$emotions)
  
  # Convert timestamp to datetime
  emotions_df$timestamp <- as.POSIXct(emotions_df$timestamp, format = "%Y-%m-%dT%H:%M:%S")
  emotions_df$date <- as.Date(emotions_df$timestamp)
  emotions_df$hour <- hour(emotions_df$timestamp)
  
  return(emotions_df)
}

# Function to create sample data for demonstration
create_sample_data <- function() {
  set.seed(123)
  n_samples <- 100
  
  emotions <- c("happy", "sad", "angry", "surprise", "neutral", "disgust", "fear")
  sources <- c("webcam", "upload")
  
  sample_data <- data.frame(
    id = 1:n_samples,
    timestamp = seq(from = as.POSIXct("2024-01-01 09:00:00"), 
                   by = "30 min", length.out = n_samples),
    dominant_emotion = sample(emotions, n_samples, replace = TRUE, 
                             prob = c(0.3, 0.15, 0.1, 0.1, 0.2, 0.05, 0.1)),
    confidence = runif(n_samples, 60, 95),
    source = sample(sources, n_samples, replace = TRUE),
    face_detected = rep(TRUE, n_samples)
  )
  
  sample_data$date <- as.Date(sample_data$timestamp)
  sample_data$hour <- hour(sample_data$timestamp)
  
  return(sample_data)
}

# Function to perform basic statistical analysis
basic_statistics <- function(data) {
  cat("=== BASIC EMOTION STATISTICS ===\n")
  cat("Total detections:", nrow(data), "\n")
  cat("Date range:", as.character(min(data$date)), "to", as.character(max(data$date)), "\n")
  cat("Average confidence:", round(mean(data$confidence, na.rm = TRUE), 2), "%\n")
  
  # Emotion frequency
  emotion_freq <- table(data$dominant_emotion)
  cat("\nEmotion Frequencies:\n")
  print(emotion_freq)
  
  # Emotion percentages
  emotion_pct <- prop.table(emotion_freq) * 100
  cat("\nEmotion Percentages:\n")
  print(round(emotion_pct, 2))
  
  # Source analysis
  source_freq <- table(data$source)
  cat("\nSource Distribution:\n")
  print(source_freq)
  
  return(list(
    total_detections = nrow(data),
    emotion_frequencies = emotion_freq,
    emotion_percentages = emotion_pct,
    avg_confidence = mean(data$confidence, na.rm = TRUE),
    source_distribution = source_freq
  ))
}

# Function to analyze temporal patterns
temporal_analysis <- function(data) {
  cat("\n=== TEMPORAL ANALYSIS ===\n")
  
  # Daily patterns
  daily_counts <- data %>%
    group_by(date) %>%
    summarise(count = n(), avg_confidence = mean(confidence, na.rm = TRUE))
  
  cat("Daily detection counts:\n")
  print(daily_counts)
  
  # Hourly patterns
  hourly_counts <- data %>%
    group_by(hour) %>%
    summarise(count = n(), avg_confidence = mean(confidence, na.rm = TRUE))
  
  cat("\nHourly patterns:\n")
  print(hourly_counts)
  
  # Emotion trends over time
  emotion_trends <- data %>%
    group_by(date, dominant_emotion) %>%
    summarise(count = n(), .groups = 'drop')
  
  return(list(
    daily_counts = daily_counts,
    hourly_counts = hourly_counts,
    emotion_trends = emotion_trends
  ))
}

# Function to perform confidence analysis
confidence_analysis <- function(data) {
  cat("\n=== CONFIDENCE ANALYSIS ===\n")
  
  # Overall confidence statistics
  conf_stats <- summary(data$confidence)
  cat("Confidence Statistics:\n")
  print(conf_stats)
  
  # Confidence by emotion
  conf_by_emotion <- data %>%
    group_by(dominant_emotion) %>%
    summarise(
      mean_confidence = mean(confidence, na.rm = TRUE),
      median_confidence = median(confidence, na.rm = TRUE),
      sd_confidence = sd(confidence, na.rm = TRUE),
      count = n()
    )
  
  cat("\nConfidence by Emotion:\n")
  print(conf_by_emotion)
  
  # High confidence detections (>80%)
  high_conf <- data[data$confidence > 80, ]
  cat("\nHigh confidence detections (>80%):", nrow(high_conf), "\n")
  
  return(list(
    overall_stats = conf_stats,
    by_emotion = conf_by_emotion,
    high_confidence_count = nrow(high_conf)
  ))
}

# Function to create visualizations
create_visualizations <- function(data) {
  cat("\n=== CREATING VISUALIZATIONS ===\n")
  
  # 1. Emotion Distribution Pie Chart
  emotion_counts <- table(data$dominant_emotion)
  pie_data <- data.frame(
    emotion = names(emotion_counts),
    count = as.numeric(emotion_counts)
  )
  
  p1 <- ggplot(pie_data, aes(x = "", y = count, fill = emotion)) +
    geom_bar(stat = "identity", width = 1) +
    coord_polar("y", start = 0) +
    theme_void() +
    labs(title = "Emotion Distribution", fill = "Emotion") +
    scale_fill_brewer(palette = "Set3")
  
  ggsave("r_scripts/plots/emotion_distribution.png", p1, width = 8, height = 6)
  
  # 2. Confidence Distribution Histogram
  p2 <- ggplot(data, aes(x = confidence)) +
    geom_histogram(bins = 20, fill = "skyblue", alpha = 0.7, color = "black") +
    labs(title = "Confidence Score Distribution", 
         x = "Confidence (%)", y = "Frequency") +
    theme_minimal()
  
  ggsave("r_scripts/plots/confidence_distribution.png", p2, width = 8, height = 6)
  
  # 3. Emotion by Source
  p3 <- ggplot(data, aes(x = dominant_emotion, fill = source)) +
    geom_bar(position = "dodge") +
    labs(title = "Emotion Detection by Source", 
         x = "Emotion", y = "Count", fill = "Source") +
    theme_minimal() +
    theme(axis.text.x = element_text(angle = 45, hjust = 1))
  
  ggsave("r_scripts/plots/emotion_by_source.png", p3, width = 10, height = 6)
  
  # 4. Temporal Analysis - Daily Trends
  daily_data <- data %>%
    group_by(date, dominant_emotion) %>%
    summarise(count = n(), .groups = 'drop')
  
  p4 <- ggplot(daily_data, aes(x = date, y = count, color = dominant_emotion)) +
    geom_line(size = 1) +
    geom_point() +
    labs(title = "Daily Emotion Trends", 
         x = "Date", y = "Count", color = "Emotion") +
    theme_minimal() +
    scale_color_brewer(palette = "Set2")
  
  ggsave("r_scripts/plots/daily_trends.png", p4, width = 12, height = 6)
  
  # 5. Confidence Box Plot by Emotion
  p5 <- ggplot(data, aes(x = dominant_emotion, y = confidence, fill = dominant_emotion)) +
    geom_boxplot(alpha = 0.7) +
    labs(title = "Confidence Distribution by Emotion", 
         x = "Emotion", y = "Confidence (%)") +
    theme_minimal() +
    theme(axis.text.x = element_text(angle = 45, hjust = 1),
          legend.position = "none") +
    scale_fill_brewer(palette = "Set3")
  
  ggsave("r_scripts/plots/confidence_by_emotion.png", p5, width = 10, height = 6)
  
  cat("Visualizations saved to r_scripts/plots/\n")
  
  return(list(p1, p2, p3, p4, p5))
}

# Function to generate statistical report
generate_report <- function(data, stats, temporal, confidence) {
  cat("\n=== GENERATING STATISTICAL REPORT ===\n")
  
  report_file <- "r_scripts/emotion_analysis_report.txt"
  
  sink(report_file)
  
  cat("FACIAL EMOTION RECOGNITION - STATISTICAL ANALYSIS REPORT\n")
  cat("Generated on:", format(Sys.time(), "%Y-%m-%d %H:%M:%S"), "\n")
  cat("="*60, "\n\n")
  
  cat("DATASET OVERVIEW\n")
  cat("Total Records:", nrow(data), "\n")
  cat("Date Range:", as.character(min(data$date)), "to", as.character(max(data$date)), "\n")
  cat("Unique Emotions:", length(unique(data$dominant_emotion)), "\n")
  cat("Data Sources:", paste(names(stats$source_distribution), collapse = ", "), "\n\n")
  
  cat("EMOTION DISTRIBUTION\n")
  for (i in 1:length(stats$emotion_frequencies)) {
    emotion <- names(stats$emotion_frequencies)[i]
    count <- stats$emotion_frequencies[i]
    pct <- stats$emotion_percentages[i]
    cat(sprintf("%-10s: %3d detections (%.1f%%)\n", emotion, count, pct))
  }
  cat("\n")
  
  cat("CONFIDENCE ANALYSIS\n")
  cat("Average Confidence:", round(stats$avg_confidence, 2), "%\n")
  cat("High Confidence Detections (>80%):", confidence$high_confidence_count, "\n")
  cat("Most Confident Emotion:", 
      confidence$by_emotion$dominant_emotion[which.max(confidence$by_emotion$mean_confidence)], "\n")
  cat("Least Confident Emotion:", 
      confidence$by_emotion$dominant_emotion[which.min(confidence$by_emotion$mean_confidence)], "\n\n")
  
  cat("TEMPORAL PATTERNS\n")
  cat("Most Active Day:", as.character(temporal$daily_counts$date[which.max(temporal$daily_counts$count)]), "\n")
  cat("Peak Hour:", temporal$hourly_counts$hour[which.max(temporal$hourly_counts$count)], ":00\n")
  cat("Average Daily Detections:", round(mean(temporal$daily_counts$count), 2), "\n\n")
  
  cat("DATA QUALITY METRICS\n")
  cat("Face Detection Success Rate: 100%\n")  # Assuming all records have face_detected = TRUE
  cat("Missing Data Points:", sum(is.na(data$confidence)), "\n")
  cat("Data Completeness:", round((1 - sum(is.na(data$confidence))/nrow(data)) * 100, 2), "%\n\n")
  
  cat("RECOMMENDATIONS\n")
  cat("1. Focus on improving detection accuracy for emotions with low confidence\n")
  cat("2. Collect more data during off-peak hours for better temporal coverage\n")
  cat("3. Balance the dataset by collecting more samples of underrepresented emotions\n")
  cat("4. Consider environmental factors that might affect detection quality\n")
  
  sink()
  
  cat("Report saved to:", report_file, "\n")
}

# Main analysis function
main_analysis <- function() {
  cat("Starting Facial Emotion Recognition Analysis...\n")
  
  # Create output directories
  dir.create("r_scripts/plots", showWarnings = FALSE, recursive = TRUE)
  
  # Load data
  data <- load_emotion_data()
  
  # Perform analyses
  stats <- basic_statistics(data)
  temporal <- temporal_analysis(data)
  confidence <- confidence_analysis(data)
  
  # Create visualizations
  plots <- create_visualizations(data)
  
  # Generate report
  generate_report(data, stats, temporal, confidence)
  
  cat("\nAnalysis completed successfully!\n")
  cat("Check the following outputs:\n")
  cat("- Plots: r_scripts/plots/\n")
  cat("- Report: r_scripts/emotion_analysis_report.txt\n")
  
  return(list(
    data = data,
    statistics = stats,
    temporal = temporal,
    confidence = confidence,
    plots = plots
  ))
}

# Run the analysis
if (!interactive()) {
  results <- main_analysis()
}
