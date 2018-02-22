import Route from '@ember/routing/route';

export default Route.extend({

    model() {
        return [
            {name: 'first'},
            {name: 'second'},
            {name: 'third'},
        ];
    },
});
