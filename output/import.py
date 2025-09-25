
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import json

# Load the data
file_path = '../data/HVDC WAREHOUSE_HITACHI(HE).xlsx'
df = pd.read_excel(file_path, sheet_name='Case List')

# Convert date columns to datetime format
date_columns = [col for col in df.columns if isinstance(col, str) and ('Date' in col or 'ETA' in col or 'ETD' in col)]
for col in date_columns:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')

# Define warehouse locations
warehouse_locations = ['DHL Warehouse', 'DSV Indoor', 'DSV Al Markaz', 'DSV Outdoor', 
                      'AAA  Storage', 'Hauler Indoor', 'DSV MZP', 'MOSB', 'Shifting', 
                      'MIR', 'SHU']

# Define site locations
site_locations = ['DAS', 'AGI']

# Function to calculate warehouse inbound flow
def calculate_warehouse_inbound(df, location):
    """
    Calculate inbound flow to a specific warehouse location
    
    Parameters:
    df (DataFrame): The dataset
    location (str): The warehouse location name
    
    Returns:
    DataFrame: Inbound flow data with source, destination, count, and dates
    """
    # Filter for cases where the location has a valid date (indicating it was received there)
    inbound_cases = df[pd.notna(df[location])]
    
    # Create a list to store inbound flow data
    inbound_flows = []
    
    for _, case in inbound_cases.iterrows():
        # Find the previous location (source of inbound flow)
        prev_location = None
        prev_date = None
        
        for loc in warehouse_locations + site_locations:
            if loc == location:
                continue
                
            if pd.notna(case[loc]) and (prev_date is None or case[loc] < case[location]):
                if prev_date is None or case[loc] > prev_date:
                    prev_location = loc
                    prev_date = case[loc]
        
        if prev_location is not None:
            inbound_flows.append({
                'case_no': case['Case No.'],
                'source': prev_location,
                'destination': location,
                'inbound_date': case[location],
                'previous_date': prev_date
            })
    
    # Convert to DataFrame
    if inbound_flows:
        inbound_df = pd.DataFrame(inbound_flows)
        return inbound_df
    else:
        return pd.DataFrame(columns=['case_no', 'source', 'destination', 'inbound_date', 'previous_date'])

# Function to calculate warehouse outbound flow
def calculate_warehouse_outbound(df, location):
    """
    Calculate outbound flow from a specific warehouse location
    
    Parameters:
    df (DataFrame): The dataset
    location (str): The warehouse location name
    
    Returns:
    DataFrame: Outbound flow data with source, destination, count, and dates
    """
    # Filter for cases that passed through this location
    outbound_cases = df[pd.notna(df[location])]
    
    # Create a list to store outbound flow data
    outbound_flows = []
    
    for _, case in outbound_cases.iterrows():
        # Find the next location (destination of outbound flow)
        next_location = None
        next_date = None
        
        for loc in warehouse_locations + site_locations:
            if loc == location:
                continue
                
            if pd.notna(case[loc]) and (next_date is None or case[loc] > case[location]):
                if next_date is None or case[loc] < next_date:
                    next_location = loc
                    next_date = case[loc]
        
        if next_location is not None:
            outbound_flows.append({
                'case_no': case['Case No.'],
                'source': location,
                'destination': next_location,
                'outbound_date': next_date,
                'source_date': case[location]
            })
    
    # Convert to DataFrame
    if outbound_flows:
        outbound_df = pd.DataFrame(outbound_flows)
        return outbound_df
    else:
        return pd.DataFrame(columns=['case_no', 'source', 'destination', 'outbound_date', 'source_date'])

# Function to calculate site inbound flow
def calculate_site_inbound(df, site_location):
    """
    Calculate inbound flow to a specific site location
    
    Parameters:
    df (DataFrame): The dataset
    site_location (str): The site location name
    
    Returns:
    DataFrame: Site inbound flow data with source, destination, count, and dates
    """
    # Filter for cases where the site location has a valid date (indicating it was received there)
    site_inbound_cases = df[pd.notna(df[site_location])]
    
    # Create a list to store site inbound flow data
    site_inbound_flows = []
    
    for _, case in site_inbound_cases.iterrows():
        # Find the previous location (source of inbound flow)
        prev_location = None
        prev_date = None
        
        for loc in warehouse_locations:
            if pd.notna(case[loc]) and (prev_date is None or case[loc] < case[site_location]):
                if prev_date is None or case[loc] > prev_date:
                    prev_location = loc
                    prev_date = case[loc]
        
        if prev_location is not None:
            site_inbound_flows.append({
                'case_no': case['Case No.'],
                'source': prev_location,
                'destination': site_location,
                'inbound_date': case[site_location],
                'previous_date': prev_date
            })
    
    # Convert to DataFrame
    if site_inbound_flows:
        site_inbound_df = pd.DataFrame(site_inbound_flows)
        return site_inbound_df
    else:
        return pd.DataFrame(columns=['case_no', 'source', 'destination', 'inbound_date', 'previous_date'])

# Function to analyze all warehouse flows
def analyze_warehouse_flows(df):
    """
    Analyze all warehouse flows (inbound and outbound) for all locations
    
    Parameters:
    df (DataFrame): The dataset
    
    Returns:
    tuple: (all_inbound_flows, all_outbound_flows, flow_summary)
    """
    all_inbound_flows = []
    all_outbound_flows = []
    
    # Calculate inbound and outbound flows for each warehouse location
    for location in warehouse_locations:
        inbound_df = calculate_warehouse_inbound(df, location)
        if not inbound_df.empty:
            inbound_df['flow_type'] = 'inbound'
            all_inbound_flows.append(inbound_df)
        
        outbound_df = calculate_warehouse_outbound(df, location)
        if not outbound_df.empty:
            outbound_df['flow_type'] = 'outbound'
            all_outbound_flows.append(outbound_df)
    
    # Calculate inbound flows for each site location
    for location in site_locations:
        site_inbound_df = calculate_site_inbound(df, location)
        if not site_inbound_df.empty:
            site_inbound_df['flow_type'] = 'site_inbound'
            all_inbound_flows.append(site_inbound_df)
    
    # Combine all flows
    combined_inbound = pd.concat(all_inbound_flows) if all_inbound_flows else pd.DataFrame()
    combined_outbound = pd.concat(all_outbound_flows) if all_outbound_flows else pd.DataFrame()
    
    # Create flow summary
    flow_summary = []
    
    # Summarize inbound flows
    if not combined_inbound.empty:
        inbound_summary = combined_inbound.groupby(['source', 'destination']).size().reset_index(name='count')
        inbound_summary['flow_type'] = 'inbound'
        flow_summary.append(inbound_summary)
    
    # Summarize outbound flows
    if not combined_outbound.empty:
        outbound_summary = combined_outbound.groupby(['source', 'destination']).size().reset_index(name='count')
        outbound_summary['flow_type'] = 'outbound'
        flow_summary.append(outbound_summary)
    
    # Combine summaries
    combined_summary = pd.concat(flow_summary) if flow_summary else pd.DataFrame()
    
    return combined_inbound, combined_outbound, combined_summary

# Execute the analysis
inbound_flows, outbound_flows, flow_summary = analyze_warehouse_flows(df)

# Display the results
print("Warehouse Flow Analysis Results:")
print("\
Top 10 Inbound Flows:")
if not inbound_flows.empty:
    inbound_counts = inbound_flows.groupby(['source', 'destination']).size().reset_index(name='count')
    inbound_counts = inbound_counts.sort_values('count', ascending=False).head(10)
    print(inbound_counts)
else:
    print("No inbound flows found.")

print("\
Top 10 Outbound Flows:")
if not outbound_flows.empty:
    outbound_counts = outbound_flows.groupby(['source', 'destination']).size().reset_index(name='count')
    outbound_counts = outbound_counts.sort_values('count', ascending=False).head(10)
    print(outbound_counts)
else:
    print("No outbound flows found.")

# Create a function to generate an interactive dashboard
def create_warehouse_flow_dashboard(inbound_flows, outbound_flows, flow_summary):
    """
    Create an interactive dashboard for warehouse flow analysis
    
    Parameters:
    inbound_flows (DataFrame): Inbound flow data
    outbound_flows (DataFrame): Outbound flow data
    flow_summary (DataFrame): Flow summary data
    
    Returns:
    str: HTML content for the dashboard
    """
    # Prepare data for charts
    
    # 1. Top 10 Warehouse Transitions
    if not flow_summary.empty:
        top_transitions = flow_summary.groupby(['source', 'destination'])['count'].sum().reset_index()
        top_transitions = top_transitions.sort_values('count', ascending=False).head(10)
        
        # Convert to format needed for ApexCharts
        transitions_data = []
        for _, row in top_transitions.iterrows():
            transitions_data.append({
                'x': f"{row['source']} to {row['destination']}",
                'y': int(row['count'])
            })
    else:
        transitions_data = []
    
    # 2. Location Flow Volume
    if not flow_summary.empty:
        # Calculate total flow volume for each location (both as source and destination)
        source_volume = flow_summary.groupby('source')['count'].sum().reset_index()
        source_volume.columns = ['location', 'outgoing']
        
        dest_volume = flow_summary.groupby('destination')['count'].sum().reset_index()
        dest_volume.columns = ['location', 'incoming']
        
        # Merge the two
        location_volume = pd.merge(source_volume, dest_volume, on='location', how='outer').fillna(0)
        location_volume['total'] = location_volume['outgoing'] + location_volume['incoming']
        location_volume = location_volume.sort_values('total', ascending=False)
        
        # Convert to format needed for ApexCharts
        locations = location_volume['location'].tolist()
        incoming_data = location_volume['incoming'].astype(int).tolist()
        outgoing_data = location_volume['outgoing'].astype(int).tolist()
    else:
        locations = []
        incoming_data = []
        outgoing_data = []
    
    # 3. Warehouse Flow Network
    if not flow_summary.empty:
        # Create a network graph
        G = nx.DiGraph()
        
        # Add nodes and edges
        for _, row in flow_summary.iterrows():
            source = row['source']
            target = row['destination']
            weight = row['count']
            
            if not G.has_edge(source, target):
                G.add_edge(source, target, weight=weight)
            else:
                G[source][target]['weight'] += weight
        
        # Get positions using a layout algorithm
        pos = nx.spring_layout(G, seed=42)
        
        # Prepare nodes and edges data for the chart
        nodes_data = []
        for node in G.nodes():
            nodes_data.append({
                'id': node,
                'x': float(pos[node][0]),
                'y': float(pos[node][1]),
                'size': 10
            })
        
        edges_data = []
        for source, target, data in G.edges(data=True):
            weight = data['weight']
            edges_data.append({
                'source': source,
                'target': target,
                'weight': int(weight)
            })
    else:
        nodes_data = []
        edges_data = []
    
    # 4. Incoming vs Outgoing Flows
    if not flow_summary.empty:
        # Get top locations by total flow
        top_locations = location_volume.head(10)['location'].tolist()
        
        # Filter flow summary for these locations
        top_flows = flow_summary[
            (flow_summary['source'].isin(top_locations)) | 
            (flow_summary['destination'].isin(top_locations))
        ]
        
        # Calculate incoming and outgoing flows for each location
        incoming_flows = {}
        outgoing_flows = {}
        
        for location in top_locations:
            incoming = top_flows[top_flows['destination'] == location]['count'].sum()
            outgoing = top_flows[top_flows['source'] == location]['count'].sum()
            
            incoming_flows[location] = int(incoming)
            outgoing_flows[location] = int(outgoing)
        
        # Convert to format needed for ApexCharts
        incoming_vs_outgoing_data = []
        
        for location in top_locations:
            incoming_vs_outgoing_data.append({
                'x': location,
                'y': [incoming_flows.get(location, 0), outgoing_flows.get(location, 0)]
            })
    else:
        incoming_vs_outgoing_data = []
    
    # Create HTML content for the dashboard
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HVDC Warehouse Flow Analysis</title>
    <link rel='stylesheet' href='https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap'>
    <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
    <style>
        body {
            font-family: 'Inter', sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
            color: #333;
        }
        .dashboard {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            padding: 20px;
        }
        .dashboard-title {
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 20px;
            color: #2c3e50;
            text-align: center;
        }
        .insights {
            background-color: #f1f8ff;
            border-left: 4px solid #4299e1;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 0 4px 4px 0;
        }
        .insights h3 {
            margin-top: 0;
            font-size: 18px;
            font-weight: 600;
            color: #2c3e50;
        }
        .insights ul {
            margin: 0;
            padding-left: 20px;
        }
        .insights li {
            margin-bottom: 8px;
        }
        .chart-container {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 20px;
        }
        .chart-box {
            flex: 1 1 calc(50% - 20px);
            min-width: 300px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            padding: 15px;
            margin-bottom: 20px;
        }
        .chart-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 15px;
            color: #2c3e50;
        }
        @media (max-width: 768px) {
            .chart-box {
                flex: 1 1 100%;
            }
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="dashboard-title">HVDC Warehouse Flow Analysis Dashboard</div>
        
        <div class="insights">
            <h3>Key Insights</h3>
            <ul>
                <li>The highest flow transition is from <strong>DSV Indoor to DSV Al Markaz</strong> with significant movement volume.</li>
                <li><strong>MOSB to DAS</strong> is another major transition path in the warehouse flow.</li>
                <li><strong>DSV Indoor</strong> is a major source location with high outgoing flows to multiple destinations.</li>
            </ul>
        </div>
        
        <div class="chart-container">
            <div class="chart-box">
                <div class="chart-title">Top 10 Warehouse Transitions</div>
                <div id="top-transitions-chart"></div>
            </div>
            
            <div class="chart-box">
                <div class="chart-title">Location Flow Volume</div>
                <div id="location-volume-chart"></div>
            </div>
        </div>
        
        <div class="chart-container">
            <div class="chart-box">
                <div class="chart-title">Warehouse Flow Network</div>
                <div id="flow-network-chart"></div>
            </div>
            
            <div class="chart-box">
                <div class="chart-title">Incoming vs Outgoing Flows</div>
                <div id="incoming-outgoing-chart"></div>
            </div>
        </div>
    </div>

    <script>
    document.addEventListener('DOMContentLoaded', function() {
        // Top 10 Warehouse Transitions Chart
        var transitionsOptions = {
            series: [{
                name: 'Flow Count',
                data: """ + json.dumps(transitions_data) + """
            }],
            chart: {
                type: 'bar',
                height: 350,
                toolbar: {
                    show: true
                },
                zoom: {
                    enabled: true
                }
            },
            plotOptions: {
                bar: {
                    horizontal: true,
                    borderRadius: 4
                }
            },
            dataLabels: {
                enabled: false
            },
            xaxis: {
                title: {
                    text: 'Number of Movements',
                    style: {
                        fontSize: '14px',
                        fontWeight: 500
                    }
                }
            },
            yaxis: {
                title: {
                    text: 'Transition Path',
                    style: {
                        fontSize: '14px',
                        fontWeight: 500
                    }
                }
            },
            colors: ['#4299e1'],
            tooltip: {
                y: {
                    formatter: function(val) {
                        return val + " movements"
                    }
                }
            },
            responsive: true
        };
        
        var transitionsChart = new ApexCharts(document.querySelector("#top-transitions-chart"), transitionsOptions);
        transitionsChart.render();
        
        // Location Flow Volume Chart
        var locationVolumeOptions = {
            series: [{
                name: 'Incoming',
                data: """ + json.dumps(incoming_data) + """
            }, {
                name: 'Outgoing',
                data: """ + json.dumps(outgoing_data) + """
            }],
            chart: {
                type: 'bar',
                height: 350,
                stacked: false,
                toolbar: {
                    show: true
                },
                zoom: {
                    enabled: true
                }
            },
            plotOptions: {
                bar: {
                    horizontal: false,
                    columnWidth: '70%',
                    borderRadius: 4
                }
            },
            dataLabels: {
                enabled: false
            },
            xaxis: {
                categories: """ + json.dumps(locations) + """,
                title: {
                    text: 'Location',
                    style: {
                        fontSize: '14px',
                        fontWeight: 500
                    }
                },
                labels: {
                    rotate: -45,
                    style: {
                        fontSize: '12px'
                    }
                }
            },
            yaxis: {
                title: {
                    text: 'Flow Count',
                    style: {
                        fontSize: '14px',
                        fontWeight: 500
                    }
                }
            },
            colors: ['#4299e1', '#48bb78'],
            legend: {
                position: 'top'
            },
            tooltip: {
                y: {
                    formatter: function(val) {
                        return val + " movements"
                    }
                }
            },
            responsive: true
        };
        
        var locationVolumeChart = new ApexCharts(document.querySelector("#location-volume-chart"), locationVolumeOptions);
        locationVolumeChart.render();
        
        // Flow Network Chart (Custom Visualization)
        var flowNetworkOptions = {
            series: [{
                name: 'Network',
                data: [0]  // Placeholder, we'll use custom rendering
            }],
            chart: {
                height: 400,
                type: 'line',  // Placeholder, we'll use custom rendering
                toolbar: {
                    show: false
                },
                zoom: {
                    enabled: false
                },
                animations: {
                    enabled: false
                },
                events: {
                    mounted: function(chart) {
                        setTimeout(function() {
                            drawNetworkGraph();
                        }, 300);
                    },
                    updated: function(chart) {
                        setTimeout(function() {
                            drawNetworkGraph();
                        }, 300);
                    }
                }
            },
            responsive: true
        };
        
        var flowNetworkChart = new ApexCharts(document.querySelector("#flow-network-chart"), flowNetworkOptions);
        flowNetworkChart.render();
        
        function drawNetworkGraph() {
            var canvas = document.createElement('canvas');
            canvas.width = document.querySelector("#flow-network-chart").offsetWidth;
            canvas.height = 400;
            canvas.style.position = 'absolute';
            canvas.style.top = '0';
            canvas.style.left = '0';
            
            document.querySelector("#flow-network-chart").innerHTML = '';
            document.querySelector("#flow-network-chart").style.position = 'relative';
            document.querySelector("#flow-network-chart").appendChild(canvas);
            
            var ctx = canvas.getContext('2d');
            var nodes = """ + json.dumps(nodes_data) + """;
            var edges = """ + json.dumps(edges_data) + """;
            
            // Scale node positions to fit canvas
            var minX = Math.min(...nodes.map(n => n.x));
            var maxX = Math.max(...nodes.map(n => n.x));
            var minY = Math.min(...nodes.map(n => n.y));
            var maxY = Math.max(...nodes.map(n => n.y));
            
            var padding = 50;
            var scaleX = (canvas.width - padding * 2) / (maxX - minX || 1);
            var scaleY = (canvas.height - padding * 2) / (maxY - minY || 1);
            
            nodes.forEach(node => {
                node.canvasX = (node.x - minX) * scaleX + padding;
                node.canvasY = (node.y - minY) * scaleY + padding;
            });
            
            // Draw edges
            edges.forEach(edge => {
                var source = nodes.find(n => n.id === edge.source);
                var target = nodes.find(n => n.id === edge.target);
                
                if (source && target) {
                    var lineWidth = Math.max(1, Math.min(5, edge.weight / 50));
                    
                    ctx.beginPath();
                    ctx.moveTo(source.canvasX, source.canvasY);
                    ctx.lineTo(target.canvasX, target.canvasY);
                    ctx.strokeStyle = 'rgba(66, 153, 225, 0.6)';
                    ctx.lineWidth = lineWidth;
                    ctx.stroke();
                    
                    // Draw arrow
                    var angle = Math.atan2(target.canvasY - source.canvasY, target.canvasX - source.canvasX);
                    var arrowLength = 10;
                    var arrowWidth = 5;
                    
                    var arrowX = target.canvasX - Math.cos(angle) * (source.size + 5);
                    var arrowY = target.canvasY - Math.sin(angle) * (source.size + 5);
                    
                    ctx.beginPath();
                    ctx.moveTo(arrowX, arrowY);
                    ctx.lineTo(
                        arrowX - arrowLength * Math.cos(angle - Math.PI/6),
                        arrowY - arrowLength * Math.sin(angle - Math.PI/6)
                    );
                    ctx.lineTo(
                        arrowX - arrowLength * Math.cos(angle + Math.PI/6),
                        arrowY - arrowLength * Math.sin(angle + Math.PI/6)
                    );
                    ctx.closePath();
                    ctx.fillStyle = 'rgba(66, 153, 225, 0.8)';
                    ctx.fill();
                    
                    // Draw weight
                    if (edge.weight > 50) {
                        var midX = (source.canvasX + target.canvasX) / 2;
                        var midY = (source.canvasY + target.canvasY) / 2;
                        
                        ctx.font = '10px Inter';
                        ctx.fillStyle = '#2c3e50';
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.fillText(edge.weight, midX, midY - 10);
                    }
                }
            });
            
            // Draw nodes
            nodes.forEach(node => {
                // Node circle
                ctx.beginPath();
                ctx.arc(node.canvasX, node.canvasY, node.size, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(66, 153, 225, 0.8)';
                ctx.fill();
                ctx.strokeStyle = '#fff';
                ctx.lineWidth = 2;
                ctx.stroke();
                
                // Node label
                ctx.font = '12px Inter';
                ctx.fillStyle = '#2c3e50';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(node.id, node.canvasX, node.canvasY + node.size + 12);
            });
            
            // Add legend
            ctx.font = '12px Inter';
            ctx.fillStyle = '#2c3e50';
            ctx.textAlign = 'left';
            ctx.textBaseline = 'middle';
            ctx.fillText('Node: Warehouse/Site Location', 10, 20);
            ctx.fillText('Edge: Flow Direction', 10, 40);
            ctx.fillText('Edge Width: Flow Volume', 10, 60);
        }
        
        // Incoming vs Outgoing Flows Chart
        var incomingOutgoingOptions = {
            series: [{
                name: 'Incoming vs Outgoing',
                data: """ + json.dumps(incoming_vs_outgoing_data) + """
            }],
            chart: {
                type: 'rangeBar',
                height: 350,
                toolbar: {
                    show: true
                },
                zoom: {
                    enabled: true
                }
            },
            plotOptions: {
                bar: {
                    horizontal: true,
                    borderRadius: 4,
                    dataLabels: {
                        position: 'top'
                    }
                }
            },
            dataLabels: {
                enabled: true,
                formatter: function(val) {
                    return val[0] === val[1] ? val[0] : val[0] + ' - ' + val[1];
                },
                style: {
                    colors: ['#fff']
                }
            },
            xaxis: {
                title: {
                    text: 'Flow Count',
                    style: {
                        fontSize: '14px',
                        fontWeight: 500
                    }
                }
            },
            yaxis: {
                title: {
                    text: 'Location',
                    style: {
                        fontSize: '14px',
                        fontWeight: 500
                    }
                }
            },
            colors: ['#4299e1'],
            legend: {
                position: 'top',
                markers: {
                    fillColors: ['#4299e1', '#48bb78']
                },
                labels: {
                    colors: ['#4299e1', '#48bb78']
                },
                customLegendItems: ['Incoming', 'Outgoing']
            },
            tooltip: {
                custom: function({series, seriesIndex, dataPointIndex, w}) {
                    var data = w.globals.initialSeries[seriesIndex].data[dataPointIndex];
                    return '<div class="arrow_box">' +
                        '<span><b>' + data.x + '</b></span><br>' +
                        '<span>Incoming: ' + data.y[0] + '</span><br>' +
                        '<span>Outgoing: ' + data.y[1] + '</span><br>' +
                        '</div>';
                }
            },
            responsive: true
        };
        
        var incomingOutgoingChart = new ApexCharts(document.querySelector("#incoming-outgoing-chart"), incomingOutgoingOptions);
        incomingOutgoingChart.render();
    });
    </script>
</body>
</html>
    """
    
    return html_content

# Generate the dashboard
dashboard_html = create_warehouse_flow_dashboard(inbound_flows, outbound_flows, flow_summary)

# Save the dashboard to a file
with open('hvdc_warehouse_flow_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(dashboard_html)

print("Dashboard generated successfully! Open 'hvdc_warehouse_flow_dashboard.html' in your browser to view the analysis.")

# Print summary statistics
print("\nSummary Statistics:")
print(f"Total inbound flows: {len(inbound_flows)}")
print(f"Total outbound flows: {len(outbound_flows)}")
print(f"Total flow summary records: {len(flow_summary)}")

if not flow_summary.empty:
    print(f"Most active flow: {flow_summary.groupby(['source', 'destination'])['count'].sum().idxmax()}")
    print(f"Highest flow count: {flow_summary.groupby(['source', 'destination'])['count'].sum().max()}")