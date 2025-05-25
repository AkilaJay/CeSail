import asyncio
import time
import tracemalloc
import argparse
import csv
import psutil
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from dom_parser.src.page_analyzer import PageAnalyzer

# Test URLs covering different types of pages
URLS = [
    "https://developer.mozilla.org/en-US/docs/Web/HTML/Element",  # Documentation
    "https://github.com",                                         # Web App
    "https://en.wikipedia.org/wiki/Web_browser",                 # Content-heavy
    "https://www.bbc.com/news",                                   # News
    "https://www.nytimes.com/",                                   # Complex layout
    "https://www.amazon.com",                                     # E-commerce
    "https://www.youtube.com",                                    # Media
    "https://www.reddit.com"                                      # Social
]

class PerformanceMetrics:
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.start_memory = self.process.memory_info().rss
        self.peak_memory = self.start_memory
        self.timings = {}
        self.elements_count = 0
        self.actions_count = 0
        self.url = ""

    def update_peak_memory(self):
        current = self.process.memory_info().rss
        self.peak_memory = max(self.peak_memory, current)
        return current

    def get_memory_usage_mb(self):
        return self.peak_memory / 1024 / 1024

async def timed_analysis(url: str, metrics: PerformanceMetrics):
    metrics.url = url
    t0 = time.perf_counter()
    
    async with PageAnalyzer() as analyzer:
        t1 = time.perf_counter()
        metrics.timings['startup'] = t1 - t0
        metrics.update_peak_memory()

        # Navigate with timeout
        try:
            await asyncio.wait_for(
                analyzer._page.goto(url, wait_until='networkidle'),
                timeout=30
            )
        except asyncio.TimeoutError:
            print(f"Warning: Navigation timeout for {url}")
        t2 = time.perf_counter()
        metrics.timings['navigation'] = t2 - t1
        metrics.update_peak_memory()

        # JS extraction
        elements_data = await analyzer._extract_elements()
        t3 = time.perf_counter()
        metrics.timings['js_extraction'] = t3 - t2
        metrics.update_peak_memory()

        # Python conversion
        elements = analyzer._convert_to_elements(elements_data)
        t4 = time.perf_counter()
        metrics.timings['python_conversion'] = t4 - t3
        metrics.elements_count = len(elements)
        metrics.update_peak_memory()

        # Action generation
        actions = await analyzer._generate_actions(elements)
        t5 = time.perf_counter()
        metrics.timings['action_generation'] = t5 - t4
        metrics.actions_count = len(actions)
        metrics.update_peak_memory()

        metrics.timings['total'] = t5 - t0

    return metrics

async def run_analysis(url: str, runs: int) -> dict:
    results = []
    for i in range(runs):
        metrics = PerformanceMetrics()
        try:
            result = await timed_analysis(url, metrics)
            results.append({
                'url': url,
                'run': i + 1,
                'total_time': result.timings['total'],
                'startup_time': result.timings['startup'],
                'navigation_time': result.timings['navigation'],
                'js_extraction_time': result.timings['js_extraction'],
                'python_conversion_time': result.timings['python_conversion'],
                'action_generation_time': result.timings['action_generation'],
                'elements_count': result.elements_count,
                'actions_count': result.actions_count,
                'peak_memory_mb': result.get_memory_usage_mb()
            })
            print(f"  Run {i+1}/{runs} completed for {url}")
        except Exception as e:
            print(f"Error analyzing {url} (run {i+1}): {str(e)}")
            continue

    # Calculate averages
    if results:
        avg = {
            'url': url,
            'runs': len(results),
            'avg_total_time': sum(r['total_time'] for r in results) / len(results),
            'avg_startup_time': sum(r['startup_time'] for r in results) / len(results),
            'avg_navigation_time': sum(r['navigation_time'] for r in results) / len(results),
            'avg_js_extraction_time': sum(r['js_extraction_time'] for r in results) / len(results),
            'avg_python_conversion_time': sum(r['python_conversion_time'] for r in results) / len(results),
            'avg_action_generation_time': sum(r['action_generation_time'] for r in results) / len(results),
            'avg_elements_count': int(sum(r['elements_count'] for r in results) / len(results)),
            'avg_actions_count': int(sum(r['actions_count'] for r in results) / len(results)),
            'avg_peak_memory_mb': sum(r['peak_memory_mb'] for r in results) / len(results)
        }
        return avg
    return None

async def main(urls, runs, output):
    print(f"\nStarting performance analysis at {datetime.now()}")
    print(f"Testing {len(urls)} URLs with {runs} runs each")
    
    # Run analyses concurrently
    tasks = [run_analysis(url, runs) for url in urls]
    results = await asyncio.gather(*tasks)
    results = [r for r in results if r is not None]

    # Print summary table
    print("\nPerformance Summary:")
    print(f"{'URL':40s} {'Total(s)':>8} {'Elements':>8} {'Actions':>8} {'Mem(MB)':>8}")
    print("-" * 80)
    for r in results:
        print(f"{r['url'][:40]:40s} {r['avg_total_time']:8.2f} {r['avg_elements_count']:8d} {r['avg_actions_count']:8d} {r['avg_peak_memory_mb']:8.1f}")

    # Save detailed results to CSV
    if output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output}_{timestamp}.csv"
        with open(filename, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
            writer.writeheader()
            for row in results:
                writer.writerow(row)
        print(f"\nDetailed results saved to {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DOM Parser Performance Test")
    parser.add_argument("--urls", nargs="*", help="List of URLs to test", default=URLS)
    parser.add_argument("--runs", type=int, default=3, help="Number of runs per URL")
    parser.add_argument("--output", type=str, default="perf_results", help="Base name for output CSV file")
    args = parser.parse_args()

    asyncio.run(main(args.urls, args.runs, args.output)) 