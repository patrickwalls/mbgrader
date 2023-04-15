var app = app || {};

// ------------------------------ //
//        NAVIGATION VIEW         //
// ------------------------------ //

app.NavigationView = Backbone.View.extend({
    
    el: '#navigation',
    
    render: function(assignment_id,question_id) {
        this.$el.html('');
        if (assignment_id) {
            $.get("/assignments/" + assignment_id, function(data) {
                var assignment_name = data.name;
                var html = "/ <a href='#assignments/" + assignment_id + "/questions'>" + assignment_name + "</a>";
                $('#navigation').prepend(html);
            });
        }
        if (question_id) {
            $.get("/assignments/" + assignment_id + "/questions/" + question_id, function(data) {
                var question_name = data.name;
                var html = " / <a href='#assignments/" + assignment_id + "/questions/" + question_id + "/batches?create=false'>" + question_name + "</a>";
                $('#navigation').append(html);
            });
        }
        return this;
    }

});

// ------------------------------ //
//        ASSIGNMENT VIEW         //
// ------------------------------ //

app.AssignmentView = Backbone.View.extend({
    
    tagName: 'tr',
    
    template: _.template($('#assignment').html()),
    
    initialize: function() {
        this.listenTo(this.model,'destroy remove',this.remove);
        this.listenTo(this.model,'sync',this.render);
    },
    
    render: function() {
        this.$el.html(this.template(this.model.attributes));
        return this;
    },
    
    events: {
        'click .grade': 'gradeAssignment',
        'click .delete': 'deleteAssignment'
    },
    
    gradeAssignment: function () {
        var url = '/assignments/' + this.model.get('id') + '/questions';
        app.AppRouter.navigate(url, {trigger: true});
    },
    
    deleteAssignment: function() {
        this.model.destroy();
    }

});

// ------------------------------ //
//        ASSIGNMENTS VIEW        //
// ------------------------------ //

app.AssignmentsView = Backbone.View.extend({
    el: '#assignments',
    
    initialize: function() {
        this.listenTo(this.collection,'sync',this.render)
    },
    
    render: function() {
        this.$('tbody').empty();
        this.collection.each(function(assignment) {
            var assignmentView = new app.AssignmentView({model: assignment});
            this.$('tbody').append(assignmentView.render().el);
        }, this);
        return this;
    },
    
    events: {
        'click #create_assignment': 'createAssignment'
    },
    
    createAssignment: function() {
        this.$('#assignment-modal-close').trigger('click');
        var name = this.$('#new_assignment_name').val();
        var folder_name = this.$('#new_assignment_folder_name').val();
        if (!name || !folder_name || _.contains(this.collection.pluck('name'),name) || _.contains(this.collection.pluck('folder_name'),folder_name)) {
            this.$('#assignment-error-modal-control').trigger('click');
            return;
        }
        this.$('#loading-submissions-modal-control').trigger('click');
        this.$('#new_assignment_name').val('');
        this.$('#new_assignment_folder_name').val('');
        this.collection.create({'name': name,'folder_name': folder_name},{
            success: function() {
                this.$('#loading-submissions-modal-control').trigger('click');
            }
        });
    }

});

// ------------------------------ //
//         QUESTION VIEW          //
// ------------------------------ //

app.QuestionView = Backbone.View.extend({
    
    tagName: 'tr',
    
    template: _.template($('#question').html()),
    
    initialize: function() {
        this.listenTo(this.model,'destroy remove',this.remove);
        this.listenTo(this.model,'sync',this.render);
    },
    
    render: function() {
        this.$el.html(this.template(this.model.attributes));
        return this;
    },
    
    events: {
        'click .delete_question': 'deleteQuestion',
        'click .create_batches': 'createBatches',
        'click .grade_batches': 'gradeBatches'
    },
    
    deleteQuestion: function() {
        this.model.destroy();
    },
    
    createBatches: function() {
        var url = '/assignments/' + this.model.get('assignment_id') + '/questions/' + this.model.get('id') + '/batches?create=true';
        app.AppRouter.navigate(url, {trigger: true});
    },
    
    gradeBatches: function() {
        var url = '/assignments/' + this.model.get('assignment_id') + '/questions/' + this.model.get('id') + '/batches?create=false';
        app.AppRouter.navigate(url, {trigger: true});
    }

});

// ------------------------------ //
//         QUESTIONS VIEW         //
// ------------------------------ //

app.QuestionsView = Backbone.View.extend({
    
    el: '#questions',
    
    initialize: function() {
        this.listenTo(this.collection,'sync',this.render);
    },
    
    render: function() {
        this.$('tbody').empty();
        this.collection.each(function(question) {
            var questionView = new app.QuestionView({model: question});
            this.$('tbody').append(questionView.render().el);
        },this);
        return this;
    },
    
    events: {
        'click #create_question': 'createQuestion',
        'click #save_grades': 'saveGrades',
        'click #get_vars': 'getVars',
        'click #create_response': 'createResponse'
    },
    
    createQuestion: function() {
        this.$('#question-modal-close').trigger('click');
        var name = this.$('#new_question_name').val();
        var var_name = this.$('#new_var_name').val();
        var alt_var_name = this.$('#new_alt_var_name').val();
        var max_grade = this.$('#new_max_grade').val();
        var tolerance = this.$('#new_tolerance').val();
        var preprocessing = this.$('#new_preprocessing').val();
        if (!name || !var_name || _.contains(this.collection.pluck('name'),name) || _.contains(this.collection.pluck('var_name'),var_name)) {
            this.$('#question-error-modal-control').trigger('click');
            return;
        }
        var question = this.collection.create(
            {
                'name': name, 'var_name': var_name, 'alt_var_name': alt_var_name, 'max_grade': max_grade,
                'tolerance': tolerance, 'preprocessing': preprocessing, 'total_batches': 0
            },
            {
                success: function() {
                    this.$('#new_question_name').val('');
                    this.$('#new_var_name').val('');
                    this.$('#new_alt_var_name').val('');
                    this.$('#new_max_grade').val('');
                    this.$('#new_tolerance').val('');
                    this.$('#new_preprocessing').val('');
                }
            });
    },
    
    saveGrades: function() {
        var url = 'assignments/' + this.collection.assignment_id + '/grades';
        $.get(url, function() {
            $('#grades-modal-control').trigger('click');
        });
    },
    
    getVars: function() {
        var url = 'assignments/' + this.collection.assignment_id + '/vars';
        $.get(url, function(data) {
            $('#vars').html(data.vars.join('<br>'));
        });
    },
    
    createResponse: function() {
        var name = this.$('#new_response_name').val();
        var vars = this.$('#new_response_vars').val();
        var expression = this.$('#new_response_expression').val();
        var extension = this.$('#new_response_extension').val();
        var data = {'name': name, 'vars': vars, 'expression': expression, 'extension': extension};
        var url = 'assignments/' + this.collection.assignment_id + '/response';
        $('#response-modal-close').trigger('click');
        $('#creating-responses-modal-control').trigger('click');
        $.post(url,data, function() {
            $('#creating-responses-modal-control').trigger('click');
        });
        this.$('#new_response_name').val('');
        this.$('#new_response_vars').val('');
        this.$('#new_response_expression').val('');
        this.$('#new_response_exstension').val('');
    }

});

// ------------------------------ //
//           BATCH VIEW           //
// ------------------------------ //

app.BatchView = Backbone.View.extend({
    
    tagName: 'tr',
    
    template: _.template($('#batch').html()),
    
    initialize: function() {
        this.listenTo(this.model,'remove',this.remove);
    },
    
    render: function() {
        this.$el.html(this.template(this.model.attributes));
        return this;
    },
    
    events: {
        'click .grade_batch': 'gradeBatch'
    },
    
    gradeBatch: function() {
        var assignment_id = this.model.get('assignment_id');
        var question_id = this.model.get('question_id');
        var batch_id = this.model.get('id');
        var url = '/assignments/' + assignment_id + '/questions/' + question_id  + '/batches/' + batch_id;
        app.AppRouter.navigate(url, {trigger: true});
    }

});

// ------------------------------ //
//          BATCHES VIEW          //
// ------------------------------ //

app.BatchesView = Backbone.View.extend({
    
    el: '#batches',
    
    initialize: function() {
        this.listenTo(this.collection,'sync',this.render);
    },
    
    render: function() {
        this.collection.each(this.renderBatch,this);
    },
    
    renderBatch: function(batch) {
        var batchView = new app.BatchView({model: batch});
        this.$('tbody').append(batchView.render().el);
    }

});

// ------------------------------ //
//          GRADING VIEW          //
// ------------------------------ //

app.GradingView = Backbone.View.extend({
    
    el: '#grading',
    
    template: _.template($('#grade').html()),
    
    initialize: function() {
        this.listenTo(this.model,'sync',this.render);
    },
    
    render: function() {
        this.$el.html(this.template(this.model.attributes));
        if (this.model.get('datatype') == 'figure') {
            var lines = this.model.get('data');
            Plotly.newPlot('data', lines);
        };
        return this;
    },
    
    events: {
        'click #next-batch': 'nextBatch',
        'click #previous-batch': 'previousBatch',
        'click #submit-batch': 'submitBatch'
    },
    
    previousBatch: function() {
        var assignment_id = this.model.get('assignment_id');
        var question_id = this.model.get('question_id');
        var previous_id = this.model.get('previous_id');
        var url = '/assignments/' + assignment_id + '/questions/' + question_id  + '/batches/' + previous_id;
        app.AppRouter.navigate(url, {trigger: true});
    },
    
    nextBatch: function() {
        var assignment_id = this.model.get('assignment_id');
        var question_id = this.model.get('question_id');
        var next_id = this.model.get('next_id');
        var url = '/assignments/' + assignment_id + '/questions/' + question_id  + '/batches/' + next_id;
        app.AppRouter.navigate(url, {trigger: true});
    },
    
    submitBatch: function() {
        var grade = $('#batch-grade').val();
        var comments = $('#batch-comments').val();
        this.model.save({'grade': grade, 'comments': comments});
    }

});