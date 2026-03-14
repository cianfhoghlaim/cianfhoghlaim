"""
Streamlit Dashboard for Receipt Evaluation System

File-based dashboard that reads pre-computed evaluation results for stability.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path
import sys

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the path so we can import our modules
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.receipt_evaluator import ReceiptEvaluator, ReceiptEvaluationResult


def initialize_session_state():
    """Initialize session state variables."""
    if 'evaluator' not in st.session_state:
        data_dir = project_root / "data"
        st.session_state.evaluator = ReceiptEvaluator(str(data_dir))
    
    if 'current_results' not in st.session_state:
        st.session_state.current_results = None
    
    if 'current_summary' not in st.session_state:
        st.session_state.current_summary = None
    
    if 'current_run_id' not in st.session_state:
        st.session_state.current_run_id = None


def load_evaluation_results(run_id: str):
    """Load evaluation results from the selected run."""
    try:
        with st.spinner(f"Loading results from run {run_id}..."):
            results, summary = st.session_state.evaluator.load_results(run_id)
            
            st.session_state.current_results = results
            st.session_state.current_summary = summary
            st.session_state.current_run_id = run_id
            
            st.success(f"✅ Loaded {len(results)} results from run {run_id}")
            
    except Exception as e:
        st.error(f"❌ Error loading results: {str(e)}")


def display_run_selector():
    """Display the run selector interface."""
    st.subheader("📂 Select Evaluation Run")
    
    # Get available runs
    available_runs = st.session_state.evaluator.list_available_runs()
    
    if not available_runs:
        st.warning("No evaluation runs found. Run evaluations using the CLI first:")
        st.code("uv run python src/receipt_evaluator.py")
        return False
    
    # Create columns for run selection
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Create a selectbox with run information
        run_options = []
        run_mapping = {}
        
        for run in available_runs:
            run_id = run['run_id']
            run_name = run.get('run_name')
            timestamp = run.get('timestamp', 'Unknown')
            total_receipts = run.get('total_receipts', 'Unknown')
            
            # Format timestamp for display
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                formatted_time = timestamp
            
            # Create display name with run name if available
            if run_name:
                display_name = f"{run_name} ({formatted_time}) - {total_receipts} receipts"
            else:
                display_name = f"{run_id} ({formatted_time}) - {total_receipts} receipts"
            
            run_options.append(display_name)
            run_mapping[display_name] = run_id
        
        selected_display = st.selectbox(
            "Select an evaluation run:",
            run_options,
            index=0 if run_options else None
        )
        
        if selected_display:
            selected_run_id = run_mapping[selected_display]
        else:
            selected_run_id = None
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        load_button = st.button("📊 Load Results", use_container_width=True, type="primary")
    
    # Load results if button clicked
    if load_button and selected_run_id:
        if selected_run_id != st.session_state.current_run_id:
            load_evaluation_results(selected_run_id)
            st.rerun()
        else:
            st.info("This run is already loaded.")
    
    return st.session_state.current_results is not None


def display_summary_statistics():
    """Display overall summary statistics."""
    if not st.session_state.current_summary:
        return
    
    stats = st.session_state.current_summary
    
    st.subheader("📊 Overall Statistics")
    
    # Create metrics columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Receipts", 
            stats.get('total_receipts', 0)
        )
    
    with col2:
        successful = stats.get('successful_extractions', 0)
        success_rate = stats.get('extraction_success_rate', 0)
        st.metric(
            "Successful Extractions", 
            successful,
            f"{success_rate:.1%}"
        )
    
    with col3:
        overall_passed = stats.get('overall_passed', 0)
        pass_rate = stats.get('overall_pass_rate', 0)
        st.metric(
            "Overall Passed", 
            overall_passed,
            f"{pass_rate:.1%}"
        )
    
    with col4:
        total = stats.get('total_receipts', 0)
        extraction_failed = total - successful
        st.metric(
            "Extraction Failures", 
            extraction_failed
        )
    
    # Display run information
    st.info(f"📅 **Run ID:** {st.session_state.current_run_id} | **Timestamp:** {stats.get('timestamp', 'Unknown')}")


def generate_evaluation_statistics_from_results():
    """Generate evaluation statistics from current results."""
    if not st.session_state.current_results:
        return {}
    
    results = st.session_state.current_results
    successful_extractions = [r for r in results if r.extraction_successful]
    
    if not successful_extractions:
        return {}
    
    # Get all unique evaluation check names
    check_names = set()
    for result in successful_extractions:
        for evaluation in result.evaluations:
            check_names.add(evaluation.check_name)
    
    # Calculate statistics for each check
    eval_stats = {}
    for check_name in check_names:
        passed_count = 0
        total_count = 0
        
        for result in successful_extractions:
            for evaluation in result.evaluations:
                if evaluation.check_name == check_name:
                    total_count += 1
                    if evaluation.passed:
                        passed_count += 1
        
        if total_count > 0:
            eval_stats[check_name] = {
                'passed': passed_count,
                'total': total_count,
                'pass_rate': passed_count / total_count
            }
    
    return eval_stats


def display_evaluation_breakdown():
    """Display evaluation breakdown by check type."""
    if not st.session_state.current_summary:
        st.warning("No summary data available.")
        return
    
    stats = st.session_state.current_summary
    eval_stats = stats.get('evaluation_statistics', {})
    
    if not eval_stats:
        st.warning("No evaluation statistics found in the summary data.")
        st.write("**Available summary keys:**", list(stats.keys()))
        
        # Try to create evaluation statistics from the results if available
        if st.session_state.current_results:
            st.info("Attempting to generate evaluation statistics from results...")
            eval_stats = generate_evaluation_statistics_from_results()
            if not eval_stats:
                st.error("Could not generate evaluation statistics from results.")
                return
        else:
            st.error("No results available to generate statistics from.")
        return
    
    st.subheader("🔍 Evaluation Breakdown")
    
    # Create DataFrame for the chart
    df_eval = pd.DataFrame([
        {
            'Check Type': check_name.replace('_', ' ').title(),
            'Passed': check_data['passed'],
            'Failed': check_data['total'] - check_data['passed'],
            'Pass Rate': check_data['pass_rate']
        }
        for check_name, check_data in eval_stats.items()
    ])
    
    # Create horizontal bar chart
    fig = px.bar(
        df_eval, 
        x=['Passed', 'Failed'], 
        y='Check Type',
        title="Evaluation Results by Check Type",
        orientation='h',
        color_discrete_map={'Passed': '#2E8B57', 'Failed': '#DC143C'}
    )
    
    fig.update_layout(
        xaxis_title="Number of Receipts",
        yaxis_title="Evaluation Check",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True, key="evaluation_breakdown_chart")
    


def load_multiple_runs(run_ids):
    """Load evaluation results for multiple runs."""
    loaded_runs = {}
    
    for run_id in run_ids:
        try:
            results, summary = st.session_state.evaluator.load_results(run_id)
            loaded_runs[run_id] = {
                'results': results,
                'summary': summary
            }
        except Exception as e:
            st.error(f"Failed to load run {run_id}: {str(e)}")
    
    return loaded_runs


def get_comparison_data(loaded_runs, selected_metrics):
    """Extract and format data for comparison across runs."""
    comparison_data = {}
    
    # Define metric display names
    metric_display_names = {
        'sum_validation': 'Sum Validation',
        'positive_values': 'Positive Values',
        'subtotal_consistency': 'Subtotal Consistency',
        'unit_price_accuracy': 'Unit Price Accuracy',
        'grand_total_calculation': 'Grand Total Calculation',
        'data_completeness': 'Data Completeness'
    }
    
    for metric in selected_metrics:
        comparison_data[metric] = {
            'display_name': metric_display_names.get(metric, metric.replace('_', ' ').title()),
            'run_data': {}
        }
        
        for run_id, run_data in loaded_runs.items():
            # Get run name for display
            run_name = run_data['summary'].get('run_name') if run_data['summary'] else None
            
            # Calculate pass rate for this metric
            results = run_data['results']
            successful_extractions = [r for r in results if r.extraction_successful]
            
            if successful_extractions:
                passed_count = 0
                total_count = 0
                
                for result in successful_extractions:
                    for evaluation in result.evaluations:
                        if evaluation.check_name == metric:
                            total_count += 1
                            if evaluation.passed:
                                passed_count += 1
                
                pass_rate = (passed_count / total_count * 100) if total_count > 0 else 0
            else:
                pass_rate = 0
            
            comparison_data[metric]['run_data'][run_id] = {
                'run_name': run_name,
                'run_id': run_id,
                'pass_rate': pass_rate
            }
    
    return comparison_data


def create_metric_comparison_chart(metric_data, metric_name):
    """Create a bar chart comparing a single metric across runs."""
    run_names = []
    pass_rates = []
    colors = []
    
    for run_id, data in metric_data['run_data'].items():
        # Use run_name from metadata if available, otherwise use run_id
        label = data['run_name'] if data['run_name'] else data['run_id']
        run_names.append(label)
        pass_rates.append(data['pass_rate'])
        
        # Color coding based on pass rate
        if data['pass_rate'] >= 80:
            colors.append('#2E8B57')  # Green for high pass rates
        elif data['pass_rate'] >= 60:
            colors.append('#FFA500')  # Orange for medium pass rates
        else:
            colors.append('#DC143C')  # Red for low pass rates
    
    fig = go.Figure(data=[
        go.Bar(
            x=run_names,
            y=pass_rates,
            marker_color=colors,
            text=[f"{rate:.1f}%" for rate in pass_rates],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title=f"{metric_data['display_name']} - Pass Rate Comparison",
        xaxis_title="Evaluation Runs",
        yaxis_title="Pass Rate (%)",
        yaxis=dict(range=[0, 100]),
        height=400,
        showlegend=False
    )
    
    return fig


def display_run_comparison():
    """Display the main run comparison interface."""
    st.subheader("🔄 Compare Evaluation Runs")
    
    # Get available runs
    available_runs = st.session_state.evaluator.list_available_runs()
    
    if len(available_runs) < 2:
        st.warning("At least 2 evaluation runs are required for comparison. Please run more evaluations first.")
        return
    
    # Create run options for selection
    run_options = {}
    for run in available_runs:
        run_id = run['run_id']
        run_name = run.get('run_name')
        timestamp = run.get('timestamp', 'Unknown')
        
        # Format timestamp for display
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            formatted_time = dt.strftime("%Y-%m-%d %H:%M")
        except:
            formatted_time = timestamp
        
        # Create display name
        if run_name:
            display_name = f"{run_name} ({formatted_time})"
        else:
            display_name = f"{run_id} ({formatted_time})"
        
        run_options[display_name] = run_id
    
    # Run selection interface
    st.subheader("📂 Select Runs to Compare")
    selected_run_displays = st.multiselect(
        "Choose 2 or more evaluation runs:",
        options=list(run_options.keys()),
        default=list(run_options.keys())[:2] if len(run_options) >= 2 else [],
        help="Select multiple runs to compare their evaluation metrics"
    )
    
    if len(selected_run_displays) < 2:
        st.info("Please select at least 2 runs to enable comparison.")
        return
    
    selected_run_ids = [run_options[display] for display in selected_run_displays]
    
    # Metric selection interface
    st.subheader("📊 Select Metrics to Compare")
    
    available_metrics = [
        'sum_validation',
        'positive_values', 
        'subtotal_consistency',
        'unit_price_accuracy',
        'grand_total_calculation',
        'data_completeness'
    ]
    
    metric_display_names = {
        'sum_validation': 'Sum Validation',
        'positive_values': 'Positive Values',
        'subtotal_consistency': 'Subtotal Consistency',
        'unit_price_accuracy': 'Unit Price Accuracy',
        'grand_total_calculation': 'Grand Total Calculation',
        'data_completeness': 'Data Completeness'
    }
    
    selected_metrics = st.multiselect(
        "Choose metrics to compare:",
        options=available_metrics,
        format_func=lambda x: metric_display_names.get(x, x.replace('_', ' ').title()),
        default=available_metrics,  # Pre-select all metrics
        help="Select which evaluation metrics you want to compare across runs"
    )
    
    if not selected_metrics:
        st.info("Please select at least one metric to compare.")
        return
    
    # Load and display comparison
    st.subheader("📈 Comparison Results")
    
    with st.spinner("Loading run data for comparison..."):
        loaded_runs = load_multiple_runs(selected_run_ids)
    
    if not loaded_runs:
        st.error("Failed to load any run data. Please check that the selected runs exist.")
        return
    
    # Get comparison data
    comparison_data = get_comparison_data(loaded_runs, selected_metrics)
    
    # Display charts
    if len(selected_metrics) == 1:
        # Single metric - full width
        metric = selected_metrics[0]
        fig = create_metric_comparison_chart(comparison_data[metric], metric)
        st.plotly_chart(fig, use_container_width=True, key=f"comparison_{metric}")
    
    elif len(selected_metrics) == 2:
        # Two metrics - side by side
        col1, col2 = st.columns(2)
        
        with col1:
            metric = selected_metrics[0]
            fig = create_metric_comparison_chart(comparison_data[metric], metric)
            st.plotly_chart(fig, use_container_width=True, key=f"comparison_{metric}")
        
        with col2:
            metric = selected_metrics[1]
            fig = create_metric_comparison_chart(comparison_data[metric], metric)
            st.plotly_chart(fig, use_container_width=True, key=f"comparison_{metric}")
    
    else:
        # Multiple metrics - grid layout
        for i in range(0, len(selected_metrics), 2):
            if i + 1 < len(selected_metrics):
                # Two charts side by side
                col1, col2 = st.columns(2)
                
                with col1:
                    metric = selected_metrics[i]
                    fig = create_metric_comparison_chart(comparison_data[metric], metric)
                    st.plotly_chart(fig, use_container_width=True, key=f"comparison_{metric}")
                
                with col2:
                    metric = selected_metrics[i + 1]
                    fig = create_metric_comparison_chart(comparison_data[metric], metric)
                    st.plotly_chart(fig, use_container_width=True, key=f"comparison_{metric}")
            else:
                # Single chart (odd number of metrics)
                metric = selected_metrics[i]
                fig = create_metric_comparison_chart(comparison_data[metric], metric)
                st.plotly_chart(fig, use_container_width=True, key=f"comparison_{metric}")
    
    # Summary table
    st.subheader("📋 Summary Table")
    
    # Create summary dataframe
    summary_data = []
    for metric in selected_metrics:
        row = {'Metric': comparison_data[metric]['display_name']}
        for run_id, data in comparison_data[metric]['run_data'].items():
            # Use run_name from metadata if available, otherwise use run_id
            column_name = data['run_name'] if data['run_name'] else data['run_id']
            row[column_name] = f"{data['pass_rate']:.1f}%"
        summary_data.append(row)
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)


def display_detailed_results():
    """Display detailed results for each receipt."""
    if not st.session_state.current_results:
        return
    
    results = st.session_state.current_results
    
    st.subheader("📋 Detailed Results")
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        status_filter = st.selectbox(
            "Filter by Status:",
            ["All", "Passed", "Failed", "Extraction Failed"]
        )
    
    with col2:
        sort_by = st.selectbox(
            "Sort by:",
            ["Receipt ID", "Pass Rate", "Status"]
        )
    
    # Filter results
    filtered_results = results.copy()
    
    if status_filter == "Passed":
        filtered_results = [r for r in results if r.overall_passed]
    elif status_filter == "Failed":
        filtered_results = [r for r in results if r.extraction_successful and not r.overall_passed]
    elif status_filter == "Extraction Failed":
        filtered_results = [r for r in results if not r.extraction_successful]
    
    # Sort results
    if sort_by == "Receipt ID":
        filtered_results.sort(key=lambda x: x.receipt_id)
    elif sort_by == "Pass Rate":
        filtered_results.sort(key=lambda x: x.pass_rate, reverse=True)
    elif sort_by == "Status":
        filtered_results.sort(key=lambda x: (x.extraction_successful, x.overall_passed), reverse=True)
    
    st.write(f"Showing {len(filtered_results)} of {len(results)} receipts")
    
    # Display results
    for result in filtered_results:
        display_receipt_result(result)


def display_receipt_result(result: ReceiptEvaluationResult):
    """Display detailed result for a single receipt."""
    # Determine status and color
    if not result.extraction_successful:
        status = "❌ Extraction Failed"
        status_color = "red"
    elif result.overall_passed:
        status = "✅ All Checks Passed"
        status_color = "green"
    else:
        status = f"⚠️ {result.pass_rate:.1%} Passed"
        status_color = "orange"
    
    # Create expandable section
    with st.expander(f"{result.receipt_id} - {status}", expanded=False):
        
        # Summary information and pass rate chart
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write(f"**Image Path:** `{Path(result.image_path).name}`")
            
            if not result.extraction_successful:
                st.error(f"**Extraction Error:** {result.extraction_error}")
            else:
                st.success("**Extraction:** Successful")
                
                if result.extracted_data:
                    st.write(f"**Transactions:** {len(result.extracted_data.transactions)}")
                    st.write(f"**Grand Total:** {result.extracted_data.grand_total}")
        
        with col2:
            if result.extraction_successful and result.evaluations:
                passed_count = sum(1 for e in result.evaluations if e.passed)
                total_count = len(result.evaluations)
                
                # Create a simple donut chart for pass rate
                fig = go.Figure(data=[go.Pie(
                    labels=['Passed', 'Failed'],
                    values=[passed_count, total_count - passed_count],
                    hole=0.5,
                    marker_colors=['#2E8B57', '#DC143C']
                )])
                
                fig.update_layout(
                    title=f"Pass Rate: {result.pass_rate:.1%}",
                    height=200,
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True, key=f"donut_chart_{result.receipt_id}")
        
        # Display evaluation details
        if result.extraction_successful and result.evaluations:
            st.write("**Evaluation Details:**")
            
            for evaluation in result.evaluations:
                if evaluation.passed:
                    st.success(f"✅ **{evaluation.check_name.replace('_', ' ').title()}:** {evaluation.message}")
                else:
                    st.error(f"❌ **{evaluation.check_name.replace('_', ' ').title()}:** {evaluation.message}")
        
        st.markdown("---")  # Separator line
        
        # Checkboxes for showing image and extracted data
        col1, col2 = st.columns(2)
        
        with col1:
            show_image = st.checkbox(f"Show receipt image", key=f"show_image_{result.receipt_id}")
        
        with col2:
            show_data = False
            if result.extraction_successful and result.extracted_data:
                show_data = st.checkbox(f"Show extracted data", key=f"show_data_{result.receipt_id}")
        
        # Show image and/or data side by side if requested
        if show_image or show_data:
            if show_image and show_data:
                # Both selected - show side by side
                img_col, data_col = st.columns(2)
                
                with img_col:
                    st.subheader("📸 Receipt Image")
                    try:
                        if Path(result.image_path).exists():
                            st.image(result.image_path, caption=f"Receipt: {result.receipt_id}", use_column_width=True)
                        else:
                            st.warning(f"⚠️ Image file not found: {result.image_path}")
                    except Exception as e:
                        st.error(f"❌ Error loading image: {str(e)}")
                
                with data_col:
                    st.subheader("📄 Extracted Data")
                    
                    # Create scrollable container for JSON data
                    json_data = {
                        "transactions": [
                            {
                                "item_name": t.item_name,
                                "quantity": t.quantity,
                                "unit_price": t.unit_price,
                                "unit_discount": t.unit_discount,
                                "total_price": t.total_price
                            } for t in result.extracted_data.transactions
                        ],
                        "subtotal": result.extracted_data.subtotal,
                        "service_charge": result.extracted_data.service_charge,
                        "tax": result.extracted_data.tax,
                        "rounding": result.extracted_data.rounding,
                        "discount_on_total": result.extracted_data.discount_on_total,
                        "grand_total": result.extracted_data.grand_total
                    }
                    
                    # Convert to formatted JSON string
                    import json as json_module
                    json_str = json_module.dumps(json_data, indent=2)
                    
                    # Display in a scrollable container with fixed height
                    st.markdown(
                        f"""
                        <div style="
                            height: 600px; 
                            overflow-y: auto; 
                            border: 1px solid #ddd; 
                            border-radius: 5px; 
                            padding: 10px; 
                            background-color: #f8f9fa;
                            font-family: 'Courier New', monospace;
                            font-size: 12px;
                            white-space: pre-wrap;
                        ">
                        {json_str}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            
            elif show_image:
                # Only image selected
                st.subheader("📸 Receipt Image")
                try:
                    if Path(result.image_path).exists():
                        st.image(result.image_path, caption=f"Receipt: {result.receipt_id}", use_column_width=True)
                    else:
                        st.warning(f"⚠️ Image file not found: {result.image_path}")
                except Exception as e:
                    st.error(f"❌ Error loading image: {str(e)}")
            
            elif show_data:
                # Only data selected
                st.subheader("📄 Extracted Data")
                st.json({
                    "transactions": [
                        {
                            "item_name": t.item_name,
                            "quantity": t.quantity,
                            "unit_price": t.unit_price,
                            "unit_discount": t.unit_discount,
                            "total_price": t.total_price
                        } for t in result.extracted_data.transactions
                    ],
                    "subtotal": result.extracted_data.subtotal,
                    "service_charge": result.extracted_data.service_charge,
                    "tax": result.extracted_data.tax,
                    "rounding": result.extracted_data.rounding,
                    "discount_on_total": result.extracted_data.discount_on_total,
                    "grand_total": result.extracted_data.grand_total
                })


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Receipt Evaluation Dashboard",
        page_icon="🧾",
        layout="wide"
    )
    
    st.title("🧾 Receipt Evaluation Dashboard")
    st.markdown("Browse and analyze pre-computed receipt evaluation results.")
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar with information and controls
    with st.sidebar:
        st.header("📖 About")
        st.markdown("""
        This dashboard displays results from receipt evaluations that have been 
        run using the CLI tool. 
        
        **To run new evaluations:**
        ```bash
        uv run python src/receipt_evaluator.py
        ```
        
        **Available evaluation checks:**
        - Sum Validation
        - Positive Values  
        - Subtotal Consistency
        - Unit Price Accuracy
        - Grand Total Calculation
        - Data Completeness
        """)
        
        st.markdown("---")
        
        # Display current results info
        if st.session_state.current_results:
            st.success(f"✅ Loaded: {st.session_state.current_run_id}")
            st.write(f"📊 {len(st.session_state.current_results)} receipts")
            
            if st.button("🔄 Clear Results", use_container_width=True):
                st.session_state.current_results = None
                st.session_state.current_summary = None
                st.session_state.current_run_id = None
                st.rerun()
        else:
            st.info("No results loaded")
        
        st.markdown("---")
        
        # CLI commands
        st.subheader("🛠️ CLI Commands")
        st.code("# Run evaluation\nuv run python src/receipt_evaluator.py")
        st.code("# List runs\nuv run python src/receipt_evaluator.py --list-runs")
        st.code("# Load specific run\nuv run python src/receipt_evaluator.py --load-run RUN_ID")
    
    # Main content
    has_results = display_run_selector()
    
    if has_results:
        # Display results
        display_summary_statistics()
        
        st.markdown("---")
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["📊 Analysis", "📋 Detailed Results", "🔄 Compare Runs"])
        
        with tab1:
            display_evaluation_breakdown()
        
        with tab2:
            display_detailed_results()
        
        with tab3:
            display_run_comparison()
    


if __name__ == "__main__":
    main()