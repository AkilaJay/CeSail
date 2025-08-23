// perf.js - Chrome Tracing compatible performance tracking

let perfEnabled = false;
let traceEvents = [];
let eventStack = [];
let eventCounter = 0;

export function enablePerf() {
  perfEnabled = true;
  traceEvents = [];
  eventStack = [];
  eventCounter = 0;
  console.log("[PERF] Chrome tracing performance tracking ENABLED");
}

export function disablePerf() {
  perfEnabled = false;
  traceEvents = [];
  eventStack = [];
  eventCounter = 0;
  console.log("[PERF] Chrome tracing performance tracking DISABLED");
}

export function perfStart(label, text) {
  if (!perfEnabled) return;
  
  const startTime = performance.now() * 1000; // Convert to microseconds for Chrome tracing
  const eventId = `event_${++eventCounter}`;
  const depth = eventStack.length; // Track nesting depth
  
  const event = {
    name: text,
    cat: label,
    ph: 'B', // Begin event
    ts: startTime,
    pid: 1,
    tid: depth, // Use depth as thread ID for visual hierarchy
    args: { 
      label, 
      text, 
      depth,
      timestamp: new Date().toISOString(),
      eventId
    }
  };
  
  traceEvents.push(event);
  eventStack.push({ 
    label, 
    eventId, 
    startTime, 
    depth,
    text 
  });
  
  console.log(`[PERF] 🟢 START: ${label} - ${text} (depth: ${depth})`);
}

export function perfEnd(label) {
  if (!perfEnabled) return;
  
  const endTime = performance.now() * 1000; // Convert to microseconds
  const stackIndex = eventStack.findIndex(item => item.label === label);
  
  if (stackIndex === -1) {
    console.warn(`[PERF] ⚠️ No matching start event found for label: ${label}`);
    return;
  }
  
  const { startTime, depth, text } = eventStack[stackIndex];
  const duration = endTime - startTime;
  eventStack.splice(stackIndex, 1);
  
  const event = {
    name: text || label,
    cat: label,
    ph: 'E', // End event
    ts: endTime,
    pid: 1,
    tid: depth, // Use depth as thread ID for visual hierarchy
    args: {
      duration: `${duration.toFixed(2)}μs`,
      durationMs: `${(duration / 1000).toFixed(2)}ms`
    }
  };
  
  traceEvents.push(event);
  
  console.log(`[PERF] 🔴 END: ${label} - ${text || label} (duration: ${(duration / 1000).toFixed(2)}ms, depth: ${depth})`);
}

export function getTraceData() {
  if (!perfEnabled) {
    console.log("[PERF] Performance tracking not enabled.");
    return null;
  }
  
  return {
    traceEvents: traceEvents,
    displayTimeUnit: 'ms',
    systemTraceEvents: 'systemTraceEvents',
    otherData: {
      totalEvents: traceEvents.length,
      maxDepth: Math.max(...eventStack.map(e => e.depth), 0),
      timestamp: new Date().toISOString()
    }
  };
}

export function saveTrace(filename = 'performance-trace.json') {
  if (!perfEnabled) {
    console.log("[PERF] Performance tracking not enabled.");
    return;
  }
  
  const traceData = getTraceData();
  if (!traceData) return;
  
  // For Node.js environment, we'll return the data to be saved by the caller
  const dataStr = JSON.stringify(traceData, null, 2);
  
  console.log(`[PERF] 📁 Trace data ready for saving as ${filename}`);
  console.log(`[PERF] 📊 Total events: ${traceData.otherData.totalEvents}`);
  console.log(`[PERF] 📊 Max depth: ${traceData.otherData.maxDepth}`);
  
  return {
    filename,
    data: dataStr,
    traceData
  };
}

export function dumpTraceToFile(filename = 'performance-trace.json') {
  if (!perfEnabled) {
    console.log("[PERF] Performance tracking not enabled.");
    return;
  }
  
  const traceData = getTraceData();
  if (!traceData) return;
  
  const dataStr = JSON.stringify(traceData, null, 2);
  
  console.log(`[PERF] 📁 Trace data ready for saving as ${filename}`);
  console.log(`[PERF] 📊 Total events: ${traceData.otherData.totalEvents}`);
  console.log(`[PERF] 📊 Max depth: ${traceData.otherData.maxDepth}`);
  console.log(`[PERF] 📊 Data size: ${(dataStr.length / 1024).toFixed(2)} KB`);
  
  // Return the data to be saved by the caller (Python/Node.js)
  return {
    filename,
    data: dataStr,
    success: true,
    fileSize: dataStr.length,
    eventCount: traceData.otherData.totalEvents,
    traceData
  };
}

export function printPerfSummary() {
  if (!perfEnabled) {
    console.log("[PERF] Performance tracking not enabled.");
    return;
  }

  console.log("========= 🕒 PERF SUMMARY =========");
  
  // Group events by category and calculate statistics
  const categories = {};
  const durations = [];
  
  for (const event of traceEvents) {
    if (event.ph === 'E') { // Only end events have duration
      const category = event.cat;
      if (!categories[category]) {
        categories[category] = { count: 0, totalDuration: 0, events: [] };
      }
      categories[category].count++;
      categories[category].events.push(event);
      
      // Calculate duration from matching start event
      const startEvent = traceEvents.find(e => 
        e.ph === 'B' && e.cat === category && e.name === event.name
      );
      if (startEvent) {
        const duration = event.ts - startEvent.ts;
        categories[category].totalDuration += duration;
        durations.push(duration);
      }
    }
  }
  
  // Print summary by category
  for (const [category, stats] of Object.entries(categories)) {
    const avgDuration = stats.totalDuration / stats.count;
    console.log(`📊 Category: ${category}`);
    console.log(`   Events: ${stats.count}`);
    console.log(`   Total Duration: ${(stats.totalDuration / 1000).toFixed(2)}ms`);
    console.log(`   Average Duration: ${(avgDuration / 1000).toFixed(2)}ms`);
    console.log('');
  }
  
  if (durations.length > 0) {
    const totalDuration = durations.reduce((sum, d) => sum + d, 0);
    const avgDuration = totalDuration / durations.length;
    const maxDuration = Math.max(...durations);
    const minDuration = Math.min(...durations);
    
    console.log(`📈 Overall Statistics:`);
    console.log(`   Total Events: ${traceEvents.length / 2}`); // Divide by 2 since each event has start+end
    console.log(`   Total Duration: ${(totalDuration / 1000).toFixed(2)}ms`);
    console.log(`   Average Duration: ${(avgDuration / 1000).toFixed(2)}ms`);
    console.log(`   Max Duration: ${(maxDuration / 1000).toFixed(2)}ms`);
    console.log(`   Min Duration: ${(minDuration / 1000).toFixed(2)}ms`);
    console.log(`   Max Depth: ${Math.max(...eventStack.map(e => e.depth), 0)}`);
  }
  
  console.log("===================================");
}

export function clearPerf() {
  traceEvents = [];
  eventStack = [];
  eventCounter = 0;
}
