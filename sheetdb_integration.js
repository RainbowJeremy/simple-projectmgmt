// Using SheetDB to connect to Google Sheets
// 1. Create a Google Sheet with columns: id, description, priority, estimate, isReady, deepCriteria
// 2. Go to https://sheetdb.io/ and connect your sheet
// 3. Get your API endpoint URL

// Load environment variables
const SHEETDB_API = window.SHEETDB_API_URL || '';

// Add all CSS in one style element
const style = document.createElement('style');
style.textContent = `
    .task-content {
        display: flex;
        flex-direction: column;
        gap: 5px;
    }
    
    .task-description {
        font-weight: 500;
    }
    
    .task-details {
        display: flex;
        gap: 10px;
        font-size: 12px;
    }
    
    .priority {
        padding: 2px 6px;
        border-radius: 3px;
        font-weight: 500;
    }
    
    .priority-high {
        background-color: #ffebee;
        color: #c62828;
    }
    
    .priority-medium {
        background-color: #fff3e0;
        color: #ef6c00;
    }
    
    .priority-low {
        background-color: #e8f5e9;
        color: #2e7d32;
    }
    
    .estimate {
        color: #666;
    }
    
    .info {
        padding: 10px;
        background-color: #e3f2fd;
        color: #1565c0;
        border-radius: 4px;
        margin: 10px 0;
        text-align: center;
    }
    
    .error {
        padding: 10px;
        background-color: #ffebee;
        color: #c62828;
        border-radius: 4px;
        margin: 10px 0;
        text-align: center;
    }

    .save-indicator {
        position: fixed;
        top: 10px;
        right: 10px;
        padding: 10px 15px;
        background-color: #f8f9fa;
        border-radius: 4px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        z-index: 1000;
    }

    .save-indicator.success {
        background-color: #d4edda;
        color: #155724;
    }

    .save-indicator.error {
        background-color: #f8d7da;
        color: #721c24;
    }

    .loading {
        padding: 20px;
        text-align: center;
        color: #6c757d;
    }

    .save-btn {
        padding: 8px 16px;
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
        transition: background-color 0.3s;
    }

    .save-btn:hover {
        background-color: #45a049;
    }

    .save-btn:disabled {
        background-color: #cccccc;
        cursor: not-allowed;
    }

    .save-btn.success {
        background-color: #4CAF50;
    }

    .save-btn.error {
        background-color: #f44336;
    }
`;
document.head.appendChild(style);

// Make functions available globally
window.loadItemsToKanban = async function() {
    try {
        console.log('Starting loadItemsToKanban...');
        const items = await testSheetDBConnection();
        
        // Clear existing tasks
        document.querySelectorAll('.task-list').forEach(list => {
            list.innerHTML = '';
        });
        
        if (items.length === 0) {
            console.log('No items found in SheetDB');
            document.querySelector('#todo .task-list').innerHTML = '<div class="info">No items found in the backlog</div>';
            return;
        }
        
        // Process each item and add to appropriate column
        items.forEach(item => {
            if (!item.id) {
                console.log('Skipping item without ID:', item);
                return;
            }
            
            // Skip items that don't have any status column set
            if (!item.toDo && !item.doing && !item.done) {
                console.log('Skipping item without status:', item.id);
                return;
            }
            
            console.log('Creating task element for item:', item);
            
            const taskEl = document.createElement('div');
            taskEl.id = item.id;
            taskEl.className = 'task';
            taskEl.draggable = true;
            
            // Determine which column to add the task to based on status columns
            let targetColumn = 'todo'; // default column
            if (item.doing) {
                targetColumn = 'doing';
            } else if (item.done) {
                targetColumn = 'done';
            }
            taskEl.dataset.column = targetColumn;
            
            // Create task content with priority and estimate
            taskEl.innerHTML = `
                <div class="task-content">
                    <div class="task-description">${item.description || ''}</div>
                    <div class="task-details">
                        <span class="priority ${(item.priority || '').toLowerCase()}">${item.priority || 'Medium'}</span>
                        <span class="estimate">${item.estimate || 'Not estimated'}</span>
                    </div>
                </div>
                <span class="delete-btn" onclick="deleteTask('${item.id}')">✕</span>
            `;
            
            // Add to appropriate column
            const columnList = document.querySelector(`#${targetColumn} .task-list`);
            if (columnList) {
                columnList.appendChild(taskEl);
                console.log(`Added task to ${targetColumn} column:`, item.id);
            } else {
                console.error(`Could not find column list for ${targetColumn}`);
            }
        });
        
        // Update task counts
        if (typeof updateTaskCounts === 'function') {
            updateTaskCounts();
        }
        console.log('Finished loading items to Kanban');
        
    } catch (error) {
        console.error('Error loading items:', error);
        // Show error message on the page
        const todoList = document.querySelector('#todo .task-list');
        if (todoList) {
            todoList.innerHTML = `<div class="error">Error loading items: ${error.message}</div>`;
        }
    }
};

// Function to test the connection to SheetDB
async function testSheetDBConnection() {
    try {
        const response = await fetch(`${SHEETDB_API}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log('Successfully connected to SheetDB');
        return data;
    } catch (error) {
        console.error('Error connecting to SheetDB:', error);
        throw error;
    }
}

// Make saveTaskStateToSheetDB available globally
window.saveTaskStateToSheetDB = async function(taskId, newColumn) {
    try {
        console.log('Attempting to save task:', { taskId, newColumn });
        
        // First get the current data to ensure we have all fields
        console.log('Fetching current data from SheetDB...');
        const getResponse = await fetch(`${SHEETDB_API}/search?id=${encodeURIComponent(taskId)}`);
        if (!getResponse.ok) {
            throw new Error(`Failed to fetch current data: ${getResponse.status}`);
        }
        const currentData = await getResponse.json();
        console.log('Current data from SheetDB:', currentData);
        
        if (currentData.length === 0) {
            throw new Error(`Task ${taskId} not found in database`);
        }
        
        const itemToUpdate = currentData[0];
        console.log('Found item to update:', itemToUpdate);
        
        // Create update object with all existing fields
        const updateData = {
            ...itemToUpdate,
            toDo: newColumn === 'todo',
            doing: newColumn === 'doing',
            done: newColumn === 'done'
        };
        
        // Send update to SheetDB using PUT with the correct endpoint
        const updateUrl = `${SHEETDB_API}/id/${encodeURIComponent(taskId)}`;
        console.log('Sending update to:', updateUrl);
        console.log('Update data:', updateData);
        
        const response = await fetch(updateUrl, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                data: [updateData]
            })
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('SheetDB response:', { status: response.status, text: errorText });
            throw new Error(`HTTP error! status: ${response.status}, response: ${errorText}`);
        }
        
        const responseData = await response.json();
        console.log('Update successful:', responseData);
        console.log(`Updated task ${taskId} to column ${newColumn}`);
    } catch (error) {
        console.error('Error saving task state:', error);
        throw error; // Re-throw to handle in the UI
    }
};

// Load backlog items from SheetDB
function loadBacklogItemsFromSheetDB() {
  // Show loading indicator
  const backlogList = document.getElementById('backlog-list');
  backlogList.innerHTML = '<div class="loading">Loading items...</div>';
  
  // Fetch data from SheetDB
  fetch(SHEETDB_API)
    .then(response => response.json())
    .then(items => {
      // Clear loading indicator
      backlogList.innerHTML = '';
      
      if (items.length === 0) {
        return; // No items to load
      }
      
      // Create item elements
      items.forEach(item => {
        if (!item.id) return; // Skip empty rows
        
        const itemEl = document.createElement('div');
        itemEl.id = item.id;
        itemEl.className = 'backlog-item';
        itemEl.draggable = true;
        
        // Parse deepCriteria
        let deepCriteria = {};
        try {
          if (item.deepCriteria) {
            deepCriteria = JSON.parse(item.deepCriteria);
          }
        } catch(e) {
          console.error('Error parsing deep criteria', e);
        }
        
        // Store deep criteria locally
        storeDeepCriteria(item.id, deepCriteria);
        
        // Priority class for styling
        const priorityClass = 'priority-' + (item.priority || '').toLowerCase();
        
        // Ready button class
        const isReady = item.isReady === 'Yes' || item.isReady === true;
        const readyClass = isReady ? 'ready-yes' : 'ready-no';
        const readyText = isReady ? 'Yes' : 'No';
        
        itemEl.innerHTML = `
          <div>${item.description}</div>
          <div class="priority ${priorityClass}">${capitalizeFirstLetter(item.priority || '')}</div>
          <div class="estimate">${item.estimate || ''}</div>
          <div class="ready"><button class="ready-btn ${readyClass}" data-item-id="${item.id}">${readyText}</button></div>
          <div class="actions"><span class="delete-btn" onclick="deleteBacklogItem('${item.id}')">✕</span></div>
        `;
        
        // Add to backlog
        backlogList.appendChild(itemEl);
        
        // Add click handler for ready button
        itemEl.querySelector('.ready-btn').addEventListener('click', (e) => {
          openDeepModal(e.target.dataset.itemId);
        });
      });
    })
    .catch(error => {
      console.error('Error loading items:', error);
      backlogList.innerHTML = '<div class="error">Error loading items. Please try again.</div>';
    });
}

// Store DEEP criteria in memory
const deepCriteriaMap = {};

function storeDeepCriteria(itemId, criteria) {
  deepCriteriaMap[itemId] = criteria;
}

function getExistingDeepCriteria(itemId) {
  return deepCriteriaMap[itemId] || null;
}

// Save backlog to SheetDB
function saveBacklogToSheetDB() {
  // Show saving indicator
  const saveIndicator = document.createElement('div');
  saveIndicator.className = 'save-indicator';
  saveIndicator.textContent = 'Saving...';
  document.body.appendChild(saveIndicator);
  
  // First, we need to delete all data
  fetch(SHEETDB_API + '/all', {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json'
    }
  })
  .then(() => {
    // Now collect and insert all current items
    const items = [];
    
    document.querySelectorAll('.backlog-item').forEach(item => {
      const itemId = item.id;
      const readyBtn = item.querySelector('.ready-btn');
      
      items.push({
        id: itemId,
        description: item.querySelector('div:first-child').textContent,
        priority: item.querySelector('.priority').textContent,
        estimate: item.querySelector('.estimate').textContent,
        isReady: readyBtn.textContent,
        deepCriteria: JSON.stringify(getExistingDeepCriteria(itemId) || {})
      });
    });
    
    // Insert new data
    return fetch(SHEETDB_API, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ data: items })
    });
  })
  .then(response => response.json())
  .then(data => {
    // Show success message
    saveIndicator.textContent = 'Saved!';
    saveIndicator.classList.add('success');
    
    // Remove indicator after a delay
    setTimeout(() => {
      saveIndicator.remove();
    }, 2000);
  })
  .catch(error => {
    console.error('Error saving:', error);
    saveIndicator.textContent = 'Save failed!';
    saveIndicator.classList.add('error');
    
    // Remove indicator after a delay
    setTimeout(() => {
      saveIndicator.remove();
    }, 3000);
  });
}

// Modify your event listeners
document.addEventListener('DOMContentLoaded', () => {
  // Load items from SheetDB
  loadBacklogItemsFromSheetDB();
  
  // Add event listeners
  document.getElementById('add-item-btn').addEventListener('click', () => {
    addBacklogItem();
    saveBacklogToSheetDB(); // Save after adding
  });
  
  document.getElementById('save-deep').addEventListener('click', () => {
    saveDeepCriteria();
    saveBacklogToSheetDB(); // Save after updating DEEP criteria
  });
  
  // Add periodic save button
  const saveBtn = document.createElement('button');
  saveBtn.className = 'btn btn-primary';
  saveBtn.textContent = 'Save to Cloud';
  saveBtn.style.position = 'fixed';
  saveBtn.style.bottom = '20px';
  saveBtn.style.right = '20px';
  saveBtn.addEventListener('click', saveBacklogToSheetDB);
  document.body.appendChild(saveBtn);
});

// Update the deleteBacklogItem function
function deleteBacklogItem(itemId) {
  if (confirm('Are you sure you want to delete this item?')) {
    const item = document.getElementById(itemId);
    item.remove();
    saveBacklogToSheetDB(); // Save after deleting
  }
}
