/* eslint-disable */
// rename this file from _test_[name] to test_[name] to activate
// and remove above this line

QUnit.test("test: Wallet", function (assert) {
	let done = assert.async();

	assert.expect(1);
	frappe.run_serially([
		() => frappe.tests.make('Wallet', [
			{key: 'value'}
		]),
		() => {
			assert.equal(cur_frm.doc.key, 'value');
		},
		() => done()
	]);

});
