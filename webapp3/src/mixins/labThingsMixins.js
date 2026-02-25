/**
 * @fileoverview
 * Global mixin providing access to the LabThings (WoT) API.
 *
 * This mixin is registered globally in `main.js` using. Do not
 * manually import it in components.
 */

import axios from "axios";
import useWotStoreModule from "@/wot-client";
import { useStore } from "@/store";
import { reactive } from "vue";

const wot = useWotStoreModule()

const state = reactive({
  pollTimers: {},
  store: () => useStore()
})

function thingDescriptions(url) {
  return wot.fetchThingDescriptions(url)
}

function thingDescription(thing) {
  return wot.thingDescription(thing);
}

function thingList() {
  return wot.thingList()
}

function thingAvailable(thing) {
  return wot.thingAvailable(thing);
}

function thingPropertyUrl(thing, property, allowUndefined = false) {
  return wot.thingPropertyUrl(
    thing,
    property,
    "readproperty",
    allowUndefined,
  );
}

function thingActionAvailable(thing, action) {
  return wot.thingAffordanceAvailable(thing, "actions", action)
}

function thingPropertyAvailable(thing, property) {
  return wot.thingAffordanceAvailable(thing, "properties", property)
}

async function readThingProperty(thing, property, _silenceErrors = false) {
  let url = wot.thingPropertyUrl(thing, property, "readproperty", false)
  try {
    let response = await axios.get(url);
    return response.data;
  } catch (error) {
    // TODO: modalError
    console.log(error)
    return undefined;
  }
}

async function writeThingProperty(thing, property, value) {
  let url = wot.thingPropertyUrl(
    thing,
    property,
    "writeproperty",
    false,
  );
  // `false` fails because axios somehow eats it!
  // Other values should not be stringified or pydantic
  // can't parse them.
  if ((value === false) | (value === true)) {
    value = JSON.stringify(value);
  }
  await axios.put(url, value);
}

async function invokeAction(thing, action, data, handleErrors = true) {
  let url = thingActionUrl(thing, action);
  try {
    let response = await axios.post(url, data);
    return response;
  } catch (error) {
    if (handleErrors) {
      // TODO: modalError
      return undefined;
    } else {
      throw error;
    }
  }
}

async function pollUntilComplete(
  taskUrl,
  ongoingMethod,
  finalMethod,
  interval = 500,
  modalErrors = true,
  emit = null
) {
  let response;
  let finalMethodCalled = false;
  try {
    response = await axios.get(taskUrl, { baseURL: state.store().baseUri });
    const result = response.data.status;

    if ((result == "running") | (result == "pending")) {
      ongoingMethod?.(response);
      state.pollTimers[taskUrl] = setTimeout(() => {
        pollUntilComplete(taskUrl, ongoingMethod, finalMethod, interval, modalErrors, emit);
      }, interval);
    } else {
      clearTimeout(state.pollTimers[taskUrl]);
      delete state.pollTimers[taskUrl];
      finalMethodCalled = true;
      finalMethod?.(response);
    }
  } catch (error) {
    if (emit != null) {
      emit("error", error);
    }
    if (modalErrors) {
      // TODO: modalError
    }
    clearTimeout(state.pollTimers[taskUrl]);
    delete state.pollTimers[taskUrl];
    if (!finalMethodCalled) {
      finalMethod?.(response);
    }
  }
}

function terminateAction(taskUrl) {
  axios.delete(taskUrl, { baseURL: state.store().baseUri });
}

async function findOngoingActions(thing, action) {
  let url = thingActionUrl(thing, action);
  try {
    return await axios.get(url);
  } catch (error) {
    console.warn("checkExistingTasks: request failed", error);
    return null;
  }
}
function thingActionUrl(thing, action, allowUndefined = false) {
  let url = wot.thingActionUrl(
    thing,
    action,
    "invokeaction",
    allowUndefined,
  );
  return url;
}

export default function useLTI() {
  return {
    thingDescriptions,
    thingDescription,
    thingList,
    thingAvailable,
    thingPropertyUrl,
    thingActionAvailable,
    thingPropertyAvailable,
    readThingProperty,
    writeThingProperty,
    invokeAction,
    pollUntilComplete,
    terminateAction,
    findOngoingActions,
    thingActionUrl,
  }
}
