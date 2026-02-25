import axios from "axios";
import { computed, reactive } from "vue";


const state = reactive({
  thingDescriptions: {},
  servient: null,
  helpers: null,
})

function addThingDescription(thingName, thingDescription) {
  state.thingDescriptions[thingName] = thingDescription
}
function removeThingDescription(thingName) {
  delete state.thingDescriptions[thingName]
}
function removeAllThingDescriptions() {
  state.thingDescriptions = {}
}

async function start() {
  // Set up thing client - not currently used.
}
async function fetchThingDescription(uri, name = null) {
  // Fetch the thing description from the given URI and consume it
  // NB this should only be called once, or we'll duplicate effort.
  // Deduplication should be done elsewhere.
  let response = await axios.get(uri);
  let td = response.data;
  let thing_name = name | uri.replace(/\/$/, "").split("/").pop();
  addThingDescription(thing_name,td)
}
async function fetchThingDescriptions(uri) {
  // Fetch thing descriptions from the given URI
  let response = await axios.get(uri);
  if (response.status != 200) throw "Could not retrieve thing descriptions";
  for (const k in response.data) {
    let thing_name = k.replace(/\/$/, "").replace(/^\//, "");
    addThingDescription(thing_name, response.data[k])
  }
}

const thingDescriptions = computed(() => {
  return state.thingDescriptions;
})
const thingList = computed(() => {
  return Object.keys(state.thingDescriptions);
})
function thingDescription(thingName) {
  return state.thingDescriptions[thingName];
}
function thingAvailable(thingName) {
  return thingName in state.thingDescriptions;
}
function thingAffordanceAvailable(thing, affordanceType, affordance) {
  let td = state.thingDescriptions[thing];
  if (!td) {
    return false;
  }
  return affordance in td[affordanceType];
}
function thingFormUrl(thing, affordanceType, affordance, op, allowUndefined = true) {
    // Find the URL for a particular operation
    let td = state.thingDescriptions[thing];
    if (!td) {
      if (allowUndefined) return undefined;
      throw `Could not find form for ${affordanceType} ${thing}/${affordance} with op ${op}`;
    }
    let affordances = td[affordanceType];

    if (!affordances || !(affordance in affordances)) {
      if (allowUndefined) return undefined;
      throw `Could not find form for ${affordanceType} ${thing}/${affordance} with op ${op}`;
    }

    let href = findFormHref(affordances[affordance], op);
    if (href == undefined) {
      if (allowUndefined) return undefined;
      throw `Could not find form for ${affordanceType} ${thing}/${affordance} with op ${op}`;
    }
    // If we've found an href, prepend the `base` URL if appropriate
    if (href.startsWith("http")) return href;
    if ("base" in td) {
      let base = td.base;
      if (href.startsWith("/")) href = href.slice(1);
      if (!base.endsWith("/")) base += "/";
      return base + href;
    }
    return href;
  }
function thingPropertyUrl(thing, property, op, allowUndefined) {
  // Find the URL for a particular property
  return thingFormUrl(thing, "properties", property, op, allowUndefined);
}
function thingActionUrl(thing, action, op, allowUndefined) {
  // Find the URL for a particular action
  return thingFormUrl(thing, "actions", action, op, allowUndefined);
}

function findFormHref(affordance, op) {
  // Find the form in the affordance that matches the given operation type
  if (affordance == undefined) return undefined;
  let forms = affordance.forms;
  let matchingForm = forms.find((f) => f.op == op || f.op.includes(op));
  if (matchingForm == undefined) return undefined;
  return matchingForm.href;
}

export default function useWotStoreModule() {
  return {
    addThingDescription,
    removeThingDescription,
    removeAllThingDescriptions,
    start,
    fetchThingDescription,
    fetchThingDescriptions,
    thingDescriptions,
    thingList,
    thingDescription,
    thingAvailable,
    thingAffordanceAvailable,
    thingFormUrl,
    thingPropertyUrl,
    thingActionUrl,
    findFormHref
  }
}
