import axios from "axios";

export const wotStoreModule = {

}

export function findFormHref(affordance, op) {
  if (affordance === undefined) return undefined;

  const forms = affordance.forms;
  const matchingForm = forms.find((f) => f.op == op || f.op.includes(op));
  if (matchingForm === undefined) return undefined;
  return matchingForm.href;
}

export default wotStoreModule;
