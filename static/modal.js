
import { h } from 'https://esm.sh/preact@10.15.1';
import htm from 'https://esm.sh/htm@3.1.1';

const html = htm.bind(h);



export default function Modal(props) {
  console.log(props.show)

  function toggle() {
    props.togM(!props.show)
  }
  const removeFirstInstance = (itemToRemove, list, setList) => {
    const index = list.indexOf(itemToRemove); // Find the index of the first instance
    if (index !== -1) { // Check if the item exists
      // Create a new array without the item
      const newItems = [
        ...list.slice(0, index), // Items before the found index
        ...list.slice(index + 1) // Items after the found index
      ];
      setList(newItems); // Update state with the new array
    }
  };

  return html`
    ${props.show === true && html`<div class="relative z-10" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true"></div>

      <div class="fixed inset-0 z-10 w-screen overflow-y-auto">
        <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
          <div class="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg">
            <div class="bg-white px-4 pb-4 pt-5 sm:p-6 sm:pb-4">
              <div class="sm:flex sm:items-start">
                <div class="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left">
                  <h3 class="text-base font-semibold leading-6 text-gray-900" id="modal-title">Your Cart</h3>
                  <div class="mt-2">
                    <ul>
                      ${props.foods.map(food => html`<li>${food}<button onclick=${() => { removeFirstInstance(food, props.foods, props.setFoods) }}>Remove</button></li>`)}
                    </ul> 
                    <p class="text-sm text-gray-500"></p>
                  </div>
                </div>
              </div>
            </div>
            <div class="bg-gray-50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6">
              <button onclick=${toggle} type="button" class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto">OK</button>
            </div>
          </div>
        </div>
      </div>
    </div>`
    }
`
}
