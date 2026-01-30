import streamlit as st
from load_source import load_source
from date_chunker import date_aware_chunk
from embeddings import vector_db
from event_extractor import extract_events
from refinement import needs_aggregation, aggregation
import json

# Page config
st.set_page_config(
    page_title="Timeline Extractor",
    page_icon="📅",
    layout="wide"
)

# Title
st.title("📅 AI Timeline Extractor")
st.markdown("Extract chronological events from Wikipedia articles or PDFs")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    source_type = st.radio(
        "Source Type:",
        ["Wikipedia URL", "PDF Upload"]
    )
    
    if source_type == "Wikipedia URL":
        source = st.text_input(
            "Wikipedia URL:",
            placeholder="https://en.wikipedia.org/wiki/..."
        )
    else:
        uploaded_file = st.file_uploader("Upload PDF", type=['pdf'])
        source = uploaded_file if uploaded_file else None
    
    query = st.text_input(
        "Query (Optional):",
        placeholder="e.g., 'career achievements'"
    )
    
    num_chunks = st.slider(
        "Number of chunks to retrieve:",
        min_value=5,
        max_value=30,
        value=15
    )
    
    enable_aggregation = st.checkbox("Enable Aggregation", value=False)
    
    extract_button = st.button("🔍 Extract Timeline", type="primary")

# Main area
if extract_button:
    if not source:
        st.error("❌ Please provide a source!")
    else:
        try:
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Load source
            status_text.text("📄 Loading source...")
            progress_bar.progress(20)
            docs = load_source(source)
            
            # Step 2: Chunk documents
            status_text.text("✂️ Chunking documents...")
            progress_bar.progress(40)
            chunks = date_aware_chunk(docs)
            
            # Step 3: Create vector database
            status_text.text("🗄️ Creating vector database...")
            progress_bar.progress(60)
            vectorstore = vector_db(chunks)
            
            # Step 4: Retrieve relevant chunks
            status_text.text("🔍 Retrieving relevant content...")
            progress_bar.progress(70)
            retriever = vectorstore.as_retriever(
                search_kwargs={"k": num_chunks}
            )
            retrieved = retriever.invoke(query if query else "timeline events")
            
            # Step 5: Extract events
         # Step 5: Extract events
            status_text.text("🤖 Extracting events with AI...")
            progress_bar.progress(85)

            events = extract_events(
                    retrieved,
                    query=query,
                    source_url=source if isinstance(source, str) else None
                )

            # Step 6: Aggregation (if enabled)
            if enable_aggregation and needs_aggregation(events):
                status_text.text("📊 Aggregating events...")
                progress_bar.progress(95)
                events = aggregation(events)
            
            progress_bar.progress(100)
            status_text.text("✅ Complete!")
            
            # Display results
            st.success(f"🎉 Extracted {len(events)} events!")
            
            # Timeline visualization
            st.markdown("---")
            st.subheader("📅 Timeline")
            
            # Sort events by year
            sorted_events = sorted(
                events,
                key=lambda e: e.get('year') if e.get('year') is not None else 9999
            )
            
            # Display events
            for i, event in enumerate(sorted_events, 1):
                year = event.get('year', 'Unknown')
                period = event.get('period', 'N/A')
                title = event.get('event_title', 'Untitled')
                desc = event.get('description', 'No description')
                confidence = event.get('confidence', 0)
                source_info = event.get('source', {})
                
                with st.expander(f"**{year}** - {title}", expanded=(i <= 3)):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**Period:** {period}")
                        st.markdown(f"**Description:** {desc}")
                        st.markdown(f"**Source:** {source_info.get('name', 'Unknown')}")
                    
                    with col2:
                        st.metric("Confidence", f"{confidence * 100:.0f}%")
            
            # Download button
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                json_data = json.dumps(events, indent=2)
                st.download_button(
                    label="📥 Download JSON",
                    data=json_data,
                    file_name="timeline_events.json",
                    mime="application/json"
                )
            
            with col2:
                # Convert to CSV-like format
                csv_data = "Year,Period,Title,Description,Confidence\n"
                for e in sorted_events:
                    csv_data += f"{e.get('year', 'N/A')},{e.get('period', 'N/A')},\"{e.get('event_title', '')}\",\"{e.get('description', '')}\",{e.get('confidence', 0)}\n"
                
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name="timeline_events.csv",
                    mime="text/csv"
                )
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.exception(e)

else:
    # Welcome message
    st.info("👈 Configure settings in the sidebar and click 'Extract Timeline' to begin")
    
    # Example
    st.markdown("### 📖 Example Queries:")
    
    st.code("https://en.wikipedia.org/wiki/Manchester_United_F.C.")