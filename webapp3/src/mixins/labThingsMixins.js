/**
 * @fileoverview
 * Global mixin providing access to the LabThings (WoT) API.
 *
 * This mixin is registered globally in `main.js` using. Do not
 * manually import it in components.
 */

import { get } from "@vueuse/core";
import axios from "axios";

let pollTimers = {};
let baseUri = "http://localhost:5000";

export default {
  data: function () {
    return {
      pollTimers: {},
      baseUri: "http://localhost:5000",
    };
  },

  methods: {
    get_data() {
      let data = {
        pollTimers: {},
        baseUri: "http://localhost:5000",
      };
      const get_baseUri = () => {
        return data.baseUri;
      };
      const get_pollTimers = (taskUrl) => {
        console.log(data.pollTimers)
        return data.pollTimers[taskUrl]
      };
      const set_pollTimers = (taskUrl, newPollTimer) => {
        data.pollTimers[taskUrl]= newPollTimer;
        console.log(data.pollTimers)
      };
      const delete_pollTimer = (taskUrl) => {
        delete data.pollTimers[taskUrl];
        console.log(data.pollTimers);
      };

      return {
        get_baseUri: get_baseUri,
        get_pollTimers: get_pollTimers,
        set_pollTimers: set_pollTimers,
        delete_pollTimer: delete_pollTimer,
      }
    },
    thingDescription(thing) {
      return this.$store.getters["wot/thingDescription"](thing);
    },
    thingList() {
      return this.$store.getters["wot/thingList"];
    },
    thingAvailable(thing) {
      return this.$store.getters["wot/thingAvailable"](thing);
    },
    thingPropertyUrl(thing, property, allowUndefined = false) {
      return this.$store.getters["wot/thingPropertyUrl"](
        thing,
        property,
        "readproperty",
        allowUndefined,
      );
    },
    thingActionAvailable(thing, action) {
      return this.$store.getters["wot/thingAffordanceAvailable"](thing, "actions", action);
    },
    thingPropertyAvailable(thing, property) {
      return this.$store.getters["wot/thingAffordanceAvailable"](thing, "properties", property);
    },
    async readThingProperty(thing, property, silenceErrors = false) {
      let url = this.$store.getters["wot/thingPropertyUrl"](thing, property, "readproperty", false);
      try {
        let response = await axios.get(url);
        return response.data;
      } catch (error) {
        if (!silenceErrors) this.modalError(error);
        return undefined;
      }
    },
    async writeThingProperty(thing, property, value) {
      let url = this.$store.getters["wot/thingPropertyUrl"](
        thing,
        property,
        "writeproperty",
        false,
      );
      // `false` fails because axios somehow eats it!
      // Other values should not be stringified or pydantic
      // can't parse them.
      if (value === false || value === true) {
        value = JSON.stringify(value);
      }
      await axios.put(url, value);
    },
    async invokeAction(thing, action, data, handleErrors = true) {
      let url = this.thingActionUrl(thing, action);
      try {
        let response = await axios.post(url, data);
        return response;
      } catch (error) {
        if (handleErrors) {
          this.modalError(error);
          return undefined;
        } else {
          throw error;
        }
      }
    },
    async pollUntilComplete(
      taskUrl,
      ongoingMethod,
      finalMethod,
      interval = 500,
      modalErrors = true,
    ) {
      let response;
      let finalMethodCalled = false;
      try {
        response = await axios.get(taskUrl, { baseURL: this.baseUri });
        const result = response.data.status;

        if (result === "running" || result === "pending") {
          ongoingMethod?.(response);
          const timer = setTimeout(() => {
            this.pollUntilComplete(taskUrl, ongoingMethod, finalMethod, interval);
          }, interval);
          this.get_data().set_pollTimers(taskUrl, timer);
        } else {
          clearTimeout(this.get_data().get_pollTimers(taskUrl));
          this.get_data().delete_pollTimer(taskUrl);
          finalMethodCalled = true;
          finalMethod?.(response);
        }
      } catch (error) {
        this.$emit("error", error);
        if (modalErrors) {
          this.modalError(error);
        }
          clearTimeout(this.get_data().get_pollTimers(taskUrl));
          this.get_data().delete_pollTimer(taskUrl);
        if (!finalMethodCalled) {
          finalMethod?.(response);
        }
      }
    },
    terminateAction(taskUrl) {
      axios.delete(taskUrl, { baseURL: this.baseUri });
    },
    async findOngoingActions(thing, action) {
      let url = this.thingActionUrl(thing, action);
      try {
        return await axios.get(url);
      } catch (error) {
        console.warn("checkExistingTasks: request failed", error);
        return null;
      }
    },
    thingActionUrl(thing, action, allowUndefined = false) {
      let url = `http://localhost:5000/${thing}/${action}`;
      return url;
    },
  },
};
