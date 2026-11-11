define(['jquery', 'core/ajax', 'core/str', 'core/notification'], function($, ajax, str, notification) {

    var TestView = {
        init: function(opts) {
            this.form = document.getElementById('chasideTestForm');
            if (!this.form) {
                return;
            }
            this.scrollToFinish = opts.scroll_to_finish;
            this.autoScrollUnanswered = opts.auto_scroll_unanswered;
            this.formChanged = false;
            this.originalValues = {};
            this.autoSaveTimer = null;

            this.bindEvents();
            this.initValues();
            
            // Auto-scroll logic from original script
            if (this.autoScrollUnanswered) {
                this.highlightFirstUnanswered();
            }
            if (this.scrollToFinish) {
                this.highlightFinishButton();
            }
        },

        initValues: function() {
            var self = this;
            var allRadios = this.form.querySelectorAll('input[type="radio"]');
            allRadios.forEach(function(radio) {
                if (radio.checked) {
                    self.originalValues[radio.name] = radio.value;
                    self.updateButtonStates(radio.name);
                }
            });
        },

        bindEvents: function() {
            var self = this;

            // Track changes for formChanged state
             document.addEventListener('change', function(e) {
                if (e.target.type === 'radio' && e.target.name.startsWith('q')) {
                    var origValue = self.originalValues[e.target.name];
                    if (origValue === undefined || origValue !== e.target.value) {
                        self.formChanged = true;
                    } else {
                         // Check if ALL values match original
                        var hasChanges = false;
                        document.querySelectorAll('input[type="radio"]:checked').forEach(function(r) {
                             if (self.originalValues[r.name] !== r.value) {
                                hasChanges = true;
                            }
                        });
                        self.formChanged = hasChanges;
                    }
                }
            });

            // Click handling deledation
            document.addEventListener('click', function(e) {
                var label = e.target.closest('label.radio-btn');
                if (!label || !self.form.contains(label)) {
                    return;
                }

                var input = label.querySelector('input[type="radio"]');
                if (!input) {
                    var forId = label.getAttribute('for');
                    if (forId) {
                        input = document.getElementById(forId);
                    }
                }

                if (!input) {
                    return;
                }

                input.checked = true;
                self.updateButtonStates(input.name);
                // Validate current page logic calls validateCurrentPage() but we don't strictly need to block user until submit. 
                // We just update states.
                
                // Trigger auto-save
                if (self.autoSaveTimer) {
                    clearTimeout(self.autoSaveTimer);
                }
                self.autoSaveTimer = setTimeout(self.autoSaveProgress.bind(self), 400);

            }, true);

            // Add change listener to radios directly as backup
            var radioInputs = this.form.querySelectorAll('input[type="radio"]');
            radioInputs.forEach(function(input) {
                input.addEventListener('change', function(e) {
                    self.updateButtonStates(this.name);
                });
            });

            // Form submit validation
            this.form.addEventListener('submit', function(e) {
                // CANCEL ANY PENDING AUTOSAVE
                if (self.autoSaveTimer) {
                    clearTimeout(self.autoSaveTimer);
                    self.autoSaveTimer = null;
                }

                var submitter = e.submitter;
                var action = submitter ? submitter.value : 'save';

                if (action !== 'next' && action !== 'finish') {
                    return true;
                }

                self.formAttempted = true;

                if (!self.validateCurrentPage()) {
                    e.preventDefault();
                    self.showUnanswered();
                    return false;
                }
            });
        },

        updateButtonStates: function(questionName) {
            var yesLabel = this.form.querySelector('label[for="' + questionName + '_yes"]');
            var noLabel = this.form.querySelector('label[for="' + questionName + '_no"]');
            var yesInput = this.form.querySelector('#' + questionName + '_yes');
            var noInput = this.form.querySelector('#' + questionName + '_no');

            if (!yesLabel || !noLabel) return;

            if (yesInput && yesInput.checked) {
                yesLabel.className = 'btn btn-primary flex-fill radio-btn chaside-btn-yes active';
                noLabel.className = 'btn btn-outline-secondary flex-fill radio-btn chaside-btn-no';
            } else if (noInput && noInput.checked) {
                noLabel.className = 'btn btn-secondary flex-fill radio-btn chaside-btn-no active';
                yesLabel.className = 'btn btn-outline-primary flex-fill radio-btn chaside-btn-yes';
            } else {
                yesLabel.className = 'btn btn-outline-primary flex-fill radio-btn chaside-btn-yes';
                noLabel.className = 'btn btn-outline-secondary flex-fill radio-btn chaside-btn-no';
            }

            var card = yesInput.closest('.card');
            if (card) {
                card.classList.remove('unanswered');
            }
        },

        autoSaveProgress: function() {
            var formData = new FormData(this.form);
            formData.set('action', 'autosave');
            
            fetch(window.location.href, {
                method: 'POST',
                body: formData
            }).catch(function(error) {
                console.log('Auto-save error:', error);
            });
        },

        validateCurrentPage: function() {
            var self = this;
            var questions = {};
            var radioInputs = this.form.querySelectorAll('input[type="radio"]');
            
            radioInputs.forEach(function(input) {
                var questionName = input.name;
                if (!questions[questionName]) {
                    questions[questionName] = false;
                }
                if (input.checked) {
                    questions[questionName] = true;
                }
            });

            return Object.values(questions).every(function(answered) {
                return answered === true;
            });
        },

        showUnanswered: function() {
            var self = this;
            var questions = {};
            var radioInputs = this.form.querySelectorAll('input[type="radio"]');
            
            radioInputs.forEach(function(input) {
                var questionName = input.name;
                if (!questions[questionName]) {
                    questions[questionName] = false;
                }
                if (input.checked) {
                    questions[questionName] = true;
                }
            });

            Object.keys(questions).forEach(function(questionName) {
                if (!questions[questionName]) {
                    var input = self.form.querySelector('input[name="' + questionName + '"]');
                    if (input) {
                        var card = input.closest('.card');
                        if (card) {
                            card.classList.add('unanswered');
                        }
                    }
                }
            });

            var firstUnanswered = document.querySelector('.card.unanswered');
            if (firstUnanswered) {
                firstUnanswered.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        },

        highlightFirstUnanswered: function() {
            setTimeout(function() {
                var questionCards = Array.from(document.querySelectorAll('.card')).filter(function(card) {
                    return card && card.id && card.id.indexOf('question-') === 0;
                });
                
                var firstUnansweredCard = questionCards.find(function(card) {
                    return !card.querySelector('input[type=radio]:checked');
                });
                
                if (firstUnansweredCard) {
                    var originalStyles = {
                        border: firstUnansweredCard.style.border,
                        backgroundColor: firstUnansweredCard.style.backgroundColor,
                        boxShadow: firstUnansweredCard.style.boxShadow
                    };
                    
                    firstUnansweredCard.style.setProperty('border', '2px solid #28a745', 'important');
                    firstUnansweredCard.style.setProperty('background-color', '#d4edda', 'important');
                    firstUnansweredCard.style.setProperty('box-shadow', '0 4px 8px rgba(40, 167, 69, 0.3)', 'important');
                    firstUnansweredCard.style.transition = 'all 0.3s ease';
                    
                    firstUnansweredCard.scrollIntoView({
                        behavior: 'smooth',
                        block: 'center'
                    });
                    
                    setTimeout(function() {
                        firstUnansweredCard.style.border = originalStyles.border;
                        firstUnansweredCard.style.backgroundColor = originalStyles.backgroundColor;
                        firstUnansweredCard.style.boxShadow = originalStyles.boxShadow;
                    }, 5000);
                }
            }, 300);
        },

        highlightFinishButton: function() {
             setTimeout(function() {
                var finishBtn = document.querySelector('button[value="finish"]');
                if (finishBtn) {
                    finishBtn.scrollIntoView({
                        behavior: 'smooth',
                        block: 'center'
                    });
                    
                    finishBtn.style.boxShadow = '0 0 20px rgba(40, 167, 69, 0.8)';
                    finishBtn.style.transition = 'all 0.3s ease';
                    
                    setTimeout(function() {
                        finishBtn.style.boxShadow = '';
                    }, 5000);
                }
            }, 300);
        }
    };

    return TestView;
});
